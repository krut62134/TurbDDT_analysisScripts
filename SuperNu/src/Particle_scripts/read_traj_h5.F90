        program readhdf5

        use hdf5

        implicit none

        character(20), parameter :: filename = "test_traj.h5"
        character(20), parameter :: dataset = "particle_dens"
        integer, parameter :: dim0 = 89
        integer, parameter :: dim1 = 81

        INTEGER(HSIZE_T), DIMENSION(2)::  data_dims

        integer :: hdferr, i, attr_num, status, error
        integer(hid_t) :: file_id, dset_id, gr_id

        real(kind = 8), dimension(dim0, dim1) :: rdata

        !Initialise HDF5 interface
        call h5open_f(hdferr)

        !Open .h5 file
        call h5fopen_f(filename, h5f_acc_rdonly_f, file_id, hdferr)

        !Get attributes info
        !call h5aget_num_attrs_f(file_id, attr_num, hdferr)
        !print *, "attr_num ",attr_num

        !Open a dataset
        call h5dopen_f(file_id, "particle_dens", dset_id, error)

        !Read dataset
        call h5dread_f(dset_id,H5T_NATIVE_DOUBLE,rdata,data_dims,error)

        !Print data in the dataset
        print *, rdata

        call h5dclose_f(dset_id, hdferr)    
        call h5fclose_f(file_id, hdferr)
        call h5close_f(hdferr)

        end program readhdf5

