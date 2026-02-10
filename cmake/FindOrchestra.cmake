
# - Find Orchestra SDK
#
#  ORCHESTRA_INCLUDE_DIR    - top-level include dir only
#  ORCHESTRA_INCLUDE_DIRS   - top-level include dir plus 3rd party Blitz dir
#  ORCHESTRA_LIBRARIES
#  ORCHESTRA_FOUND
#
# © 2015 Joseph Naegele
#
# updated in 2017 by V. R. to handle 2017 (1.7-1) Orchestra layout
#
# and in 2020 for Orchestra 1.8-1 layout

set (ORCHESTRA_TOPDIR $ENV{SDKTOP})

set (ORCHESTRA_INCLUDE_DIR  ${ORCHESTRA_TOPDIR}/include  ${ORCHESTRA_TOPDIR}/include/lx/include/)
set (ORCHESTRA_INCLUDE_DIRS ${ORCHESTRA_TOPDIR}/3p/      ${ORCHESTRA_TOPDIR}/include/recon/)

foreach(libs

         AcquiredData.a
         AcquiredDataApplication.a
         AcquiredDataSupport.a
         Acquisition.a
         Arc.a
         Asset.a
         AssetPipeline.a
         BiasCorrection.a
         Calibration3D.a
         CalibrationCommon.a
         Cartesian2D.a
         Cartesian2DDataHandling.a
         Cartesian3D.a
         Cartesian3DDataHandling.a
         Cine.a
         Clariview.a
         Common.a
         Control.a
         CorePipeline.a
         DefineFilter.a
         Dicom.a
         Disco.a
         Epi.a
         EpiDataHandling.a
         EpiDiffusion.a
         EpiDistortionCorrection.a
         EpiReferenceScan.a
         Flex.a
         Foundation.a
         FrameDownSampler.a
         Gradwarp.a
         Hdf5.a
         Legacy.a
         LegacySupport.a
         LiveSupportCloud.a
         LiveSupportDeployment.a
         LiveSupportProcessing.a
         LiveSupportShared.a
         Maestro.a
         Math.a
         MoCo.a
         MoCoSupport.a
         OrchestraCrucial.a
         OrchestraMaestro.a
         OrchestraMaestroSupport.a
         PhaseContrast.a
         ProcessingControl.a
         ProcessingFlow.a
         Pure1.a
         Pure2.a
         ReceiveChainConfig.a
         ScanArchiveConverterUtils.a
         Scic.a
         SoloSupport.a
         SpectroCommon.a
         SpectroMCSI.a
         SpectroMCSILegacy.a
         SpectroMultiVoxel.a
         SpectroSingleVoxel.a
         Spiral.a
         System.a
         SystemServices.a
         TestSupport.a
         Tricks.a
         Core.a   # Needs to remain last on linkage list b/c of dependencies on previously listed libraries.
       )

    # list(APPEND ORCHESTRA_LIBRARIES $ENV{SDKTOP}/lib/lib${libs}.a)

    message("Finding library: lib${libs}")

    list(APPEND ORCHESTRA_LIBRARIES $ENV{SDKTOP}/lib/lib${libs})

endforeach()

# Orchestra HDF5 libraries
foreach(lib h5tools hdf5_cpp hdf5 Hdf5                                                             # HDF libraries
            dcmdata dcmnet dcmtls oflog ofstd ssl crypto                                           # DCMTK   "
            fftw3f fftw3                                                                           # FFTW3   "
            boost_date_time boost_program_options boost_filesystem boost_regex boost_serialization # BOOST   "
            boost_wserialization boost_thread boost_system                                         # BOOST   "
            lapack blas f2c                                                                        # LAPACK  "
            blitz)                                                                                 # BLITZ   "
    # find_library(ORCHESTRA_BOOST_${lib}_LIBRARY "boost_${lib}"                                     # Pattern for finding library with
                                                                                                     # common prefix, e.g. 'boost_' here.
    find_library(ORCHESTRA_SUPPORT_${lib}_LIBRARY ${lib}
        PATHS ${ORCHESTRA_TOPDIR}   ${ORCHESTRA_TOPDIR}/3p
        PATH_SUFFIXES lib lib64
        NO_DEFAULT_PATH)
    mark_as_advanced(${ORCHESTRA_SUPPORT_${lib}_LIBRARY})
    list(APPEND ORCHESTRA_LIBRARIES ${ORCHESTRA_SUPPORT_${lib}_LIBRARY})
endforeach()

# Orchestra Blitz include dir
find_path(ORCHESTRA_BLITZ_INCLUDE_DIR blitz/blitz.h
    PATHS ${ORCHESTRA_TOPDIR}   ${ORCHESTRA_TOPDIR}/3p
    PATH_SUFFIXES include)
if(ORCHESTRA_BLITZ_INCLUDE_DIR)
    mark_as_advanced(${ORCHESTRA_BLITZ_INCLUDE_DIR})
    list(APPEND ORCHESTRA_INCLUDE_DIRS ${ORCHESTRA_BLITZ_INCLUDE_DIR})
endif()

link_directories (${ORCHESTRA_TOPDIR}/lib   ${ORCHESTRA_TOPDIR}/3p/lib   ${ORCHESTRA_TOPDIR}/3p/lib64)

include_directories (${ORCHESTRA_INCLUDE_DIR} ${ORCHESTRA_INCLUDE_DIRS})

message("Orchestra Install Root: $ENV{SDKTOP}")
message("Orchestra Top Dir:      ${ORCHESTRA_TOPDIR}")
message("Orchestra Include Dir:  ${ORCHESTRA_INCLUDE_DIR}")
message("Orchestra Include Dirs: ${ORCHESTRA_INCLUDE_DIRS}")
message("Orchestra Libraries:    ${ORCHESTRA_LIBRARIES}")

list(APPEND ORCHESTRA_LIBRARIES pthread z dl)

set(ORCHESTRA_DEFINITIONS -w -pthread -DGE_64BIT -DEXCLUDE_RSP_TYPE_DEFINES -D_GE_ESE_BUILD)

INCLUDE("FindPackageHandleStandardArgs")
FIND_PACKAGE_HANDLE_STANDARD_ARGS("Orchestra"
    "GE Orchestra SDK NOT FOUND. Try setting $SDKTOP environment variable"
    ORCHESTRA_INCLUDE_DIR ORCHESTRA_INCLUDE_DIRS ORCHESTRA_LIBRARIES ORCHESTRA_DEFINITIONS)

MARK_AS_ADVANCED(ORCHESTRA_INCLUDE_DIR ORCHESTRA_INCLUDE_DIRS ORCHESTRA_LIBRARIES)

