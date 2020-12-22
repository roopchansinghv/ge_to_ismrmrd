
import   numpy          as       np
import   ismrmrd        as       mrd
import   ismrmrd.xsd
from     matplotlib     import   pyplot   as plt



class rawMRutils:



   # def __init__ (self):



   def returnHeaderAndData (h5RawFilePath, dataElement='/dataset'):
  
      '''
         Given an ISMRMRD data file, return a tuple with the first
         element being the XML header serialized into a structure,
         and the 2nd element a Numpy array with the indices ordered
         according to the following shape:

         [coil, readout, phase_encode_1, phase_encode_2 or slice, time or contrast]
      '''

      rawDataArray = mrd.Dataset(h5RawFilePath, dataElement, True)
      rawDataArrayHeader = ismrmrd.xsd.CreateFromDocument(rawDataArray.read_xml_header())

      enc = rawDataArrayHeader.encoding[0]

      # Matrix size
      eNx = enc.encodedSpace.matrixSize.x
      eNy = enc.encodedSpace.matrixSize.y
      # eNz = enc.encodedSpace.matrixSize.z

      if enc.encodingLimits.slice != None:
         eNz = enc.encodingLimits.slice.maximum + 1
      else:
         eNz = 1

      if enc.encodingLimits.repetition != None:
         eNt = enc.encodingLimits.repetition.maximum + 1
      else:
         eNt = 1

      # This will pack k-space data into a numpy array with the following
      # data order / shape:
      #
      #    [coil, readout, phase_encode_1, phase_encode_2 or slice, time]
      #
      # This ordering may not be suitable for all, or even a majority of
      # applications.  But since this is a demonstration notebook, it
      # seemed to be a 'natural' way to unpack and organize the data from
      # the ISMRMRD raw file.

      allKspace = np.zeros((rawDataArray.read_acquisition(0).data.shape[0],
                            rawDataArray.read_acquisition(0).data.shape[1],
                            eNy, eNz, eNt), dtype=np.complex64)

      traj = rawDataArrayHeader.encoding[0].trajectory
      if (traj == 'epi'):
         trajID = rawDataArrayHeader.encoding[0].trajectoryDescription.identifier
         if (trajID == 'ConventionalEPI'):
            print ("Trajectory for this dataset is %s, and trajectory ID is %s" % (traj, trajID))

            # Iterate over the elements of the trajectory section, and get 'long' parameters needed for EPI.
            for i, trajValue in enumerate(rawDataArrayHeader.encoding[0].trajectoryDescription.userParameterLong[:]):
               print ("Variable %20s has value %05s" % (trajValue.orderedContent()[0].value,
                                                    str(trajValue.orderedContent()[1].value)))

               # Can replace below with a 'switch' statement if more EPI parameters need to be extracted
               # and returned here.
               #
               # Can also access each parameter name via ...userParameterLong[i].name, i.e. trajValue.name,
               # though trajValue does not return a usable value, which is why .orderedContent()[n].value is
               # being used here.
               if (trajValue.name == 'numberOfNavigators'):
                  numEPInavs = trajValue.orderedContent()[1].value

            refData    = np.zeros((rawDataArray.read_acquisition(0).data.shape[0],
                                   rawDataArray.read_acquisition(0).data.shape[1],
                                   numEPInavs, eNz, eNt), dtype=np.complex64)

            refCounter = np.zeros((eNz, eNt), dtype=int)

      for i in range(rawDataArray.number_of_acquisitions()):
         thisAcq = rawDataArray.read_acquisition(i)

         slice   = thisAcq.idx.slice
         rep     = thisAcq.idx.repetition

         # Check if data is "reverse" in direction in acquisition - flag 22.  If so, reverse order of loading.
         if (thisAcq.is_flag_set(22)): # 22 == ISMRMRD_ACQ_IS_REVERSE flag
            thisData = thisAcq.data[:,::-1] # First dimension of data *IS* channels, then number of readout points.
         else:
            thisData = thisAcq.data

         # If acqusition doesn't contain image navigator data, store with regular image data
         if not (thisAcq.is_flag_set(24)): # 24 == ACQ_IS_PHASECORR_DATA flag - need to figure out how to include definition
            allKspace[:, :, thisAcq.idx.kspace_encode_step_1, slice, rep] = thisData
         else:
            refData  [:, :, refCounter[slice, rep],           slice, rep] = thisData
            refCounter[slice,rep] += 1

      if (traj == 'epi'):
         if (rawDataArrayHeader.encoding[0].trajectoryDescription.identifier == 'ConventionalEPI'):
            return rawDataArrayHeader, allKspace, refData
      else:
         return rawDataArrayHeader, allKspace



   def computeAndPlot (arraySent2Plot, quant='magnitude', coil=-1, cmap='viridis'):

      '''
         Convenience function for organizing complex data array and plotting an
         image derived from that data.

         It is possible to select a particular element from multi-channel/coil
         data.

         It is also to select whether magnitude or phase data is displayed.  To
         do - add options for I and Q components of complext data.

         Also possible to select the matplotlib color map used to represent /
         display data.
      '''

      # print ("shape of sent array is: ", arraySent2Plot.shape)

      if (coil == -1):
         array2Plot = arraySent2Plot
      else:
         array2Plot = np.squeeze(arraySent2Plot[coil, :, :, :, :])

      # print ("shape of plotted array is: ", array2Plot.shape)

      # from comment above, the next to last index is
      # the slice slot, while the last index is
      #  repetition / contrast.
      slices2Plot = array2Plot.shape[-2]
      times2Plot  = array2Plot.shape[-1]

      # print ("slices:   ", slices2Plot)
      # print ("time pts: ", times2Plot)

      imageCols = int(np.ceil(np.sqrt(slices2Plot)))
      imageRows = int(np.ceil(np.sqrt(slices2Plot))) * times2Plot

      plottedFigures = plt.figure(figsize=(12,18))

      for t in range(times2Plot):
         for s in range(slices2Plot):
            subImages = plottedFigures.add_subplot(imageRows, imageCols, ((t * imageRows * imageCols / times2Plot) + s + 1))

            if ((quant == 'angle') or (quant == 'phase')):
               if (coil == -1):
                  reconnedImage = np.sum(np.angle(array2Plot[:, :, :, s, t]), axis=0)
               else:
                  reconnedImage = (np.angle(array2Plot[:, :, s, t]))
            else:
               if (coil == -1):
                  reconnedImage = np.sqrt(np.sum((abs(array2Plot[:, :, :, s, t])), axis=0))
               else:
                  reconnedImage = np.sqrt(((abs(array2Plot[:, :, s, t]))))

            subImages.imshow(reconnedImage, cmap)



   def plotProfile (lines2Plot, quant='magnitude'):

      '''
         Routine to leverage matplotlib to plot magnitude or phase profile of
         particular lines of data sent in the 'lines2Plot' variable.

         The variable passed should be a single line or series of lines of
         complex points.  The data to plot should be in the first dimension of
         the array, and the lines indexed are in the second dimension.
      '''

      fig, ax = plt.subplots(1, 1, sharex=True, sharey=True)

      if ((quant == 'angle') or (quant == 'phase')):
         ax.plot(np.angle(lines2Plot), label=quant)
      else: # plot magnitude of lines
         ax.plot(np.abs(lines2Plot),   label=quant)

      ax.legend()

