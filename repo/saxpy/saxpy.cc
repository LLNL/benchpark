#include <iostream>
#include <unistd.h>
#include <mpi.h>
#ifdef USE_CUDA
#include <cuda_runtime.h>
#define MEMALLOC(x, size)            cudaMalloc(&x, size)
#define MEMCOPY(da, ha, size, xmode) cudaMemcpy(da, ha, size, xmode)
#define MEMFREE(da)                  cudaFree(da)
#define HTOD                         cudaMemcpyHostToDevice
#define DTOH                         cudaMemcpyDeviceToHost
#define KERNEL(kernel, dr, dx, dy, n) kernel<<<NB, NT>>>(dr, dx, dy, n)
#define DEVICE __device__
#define GLOBAL __global__
#elif USE_HIP
#include <hip/hip_runtime.h>
#define MEMALLOC(x, size)            hipMalloc(&x, size)
#define MEMCOPY(da, ha, size, xmode) hipMemcpy(da, ha, size, xmode)
#define MEMFREE(da)                  hipFree(da)
#define HTOD     hipMemcpyHostToDevice
#define DTOH     hipMemcpyDeviceToHost
#define KERNEL(kernel, dr, dx, dy, n) hipLaunchKernelGGL(kernel, dim3(NB), dim3(NT), 0, 0, dr, dx, dy, n)
#define DEVICE __device__
#define GLOBAL __global__
#elif USE_OPENMP
#include <omp.h>
#define MEMALLOC(x, size)
#define MEMCOPY(da, ha, size, xmode) da = ha
#define MEMFREE(da)
#define HTOD
#define DTOH
#define KERNEL(kernel, dr, dx, dy, n) kernel(dr, dx, dy, n)
#define DEVICE
#define GLOBAL
#else
#define MEMALLOC(x, size)
#define MEMCOPY(da, ha, size, xmode) da = ha
#define MEMFREE(da)
#define HTOD
#define DTOH
#define KERNEL(kernel, dr, dx, dy, n) kernel(dr, dx, dy, n)
#define DEVICE
#define GLOBAL
#endif

constexpr int NB = 4;
constexpr int NT = 256;

using DTYPE=float;

DEVICE inline DTYPE saxpy(DTYPE xi, DTYPE yi) {
  return 3.14 * xi + yi;
}

#if defined (USE_CUDA) || defined (USE_HIP)
GLOBAL void saxpy_kernel(DTYPE *r, DTYPE *x, DTYPE *y, int size) {
    int tid = blockIdx.x * blockDim.x + threadIdx.x;
    if (tid < size) {
        r[tid] = saxpy(x[tid], y[tid]);
    }
}
#else
void saxpy_kernel(DTYPE *r, DTYPE *x, DTYPE *y, int size) {
#ifdef USE_OPENMP
    #pragma omp parallel for
#endif
    for (int i = 0; i < size; ++i) {
        r[i] = saxpy(x[i], y[i]);
    }
}
#endif

int main(int argc, char** argv) {
    int opt;
    int N = 0;

    while ((opt = getopt(argc, argv, "n:")) != -1) {
        switch (opt) {
            case 'n':
                N = atoi(optarg);
                fprintf(stdout, "Problem size: %d\n", N);
                break;
            case '?':
                fprintf(stderr, "Unknown option -%c.\n", optopt);
                return 1;
            default:
                return 1;
        }
    }

    int rank, size;
    MPI_Init(&argc, &argv);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    DTYPE *h_x, *h_y, *h_r;
    DTYPE *d_x, *d_y, *d_r;
    size_t nbytes = N * sizeof(DTYPE);

    h_x = new DTYPE[N];
    h_y = new DTYPE[N];
    h_r = new DTYPE[N];

    for (int i = 0; i < N; ++i) {
      h_x[i] = i;
      h_y[i] = i*i;
    }

    MEMALLOC(d_x, nbytes);
    MEMALLOC(d_y, nbytes);
    MEMALLOC(d_r, nbytes);

    MEMCOPY(d_x, h_x, nbytes, HTOD);
    MEMCOPY(d_y, h_y, nbytes, HTOD);

    KERNEL(saxpy_kernel, d_r, d_x, d_y, N);

    MEMCOPY(h_r, d_r, nbytes, DTOH);

    MEMFREE(d_x);
    MEMFREE(d_y);
    MEMFREE(d_r);

    std::cout << "Kernel done (" << rank << "): " << N << std::endl;

    delete[] h_x;
    delete[] h_y;
    delete[] h_r;

    MPI_Finalize();
    return 0;
}
