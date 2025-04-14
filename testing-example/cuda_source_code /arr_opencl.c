#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <CL/cl.h>
#include <iostream>
#include <fstream>


#define MAX_SOURCE_SIZE (0x100000)
#define NUM_WORK_ITEMS 8  // Fixed to 8 threads

// Function to read the kernel file
char* read_kernel_file(const char* filename) {
    FILE *fp;
    char *source_str;
    size_t source_size;

    fp = fopen(filename, "r");
    if (!fp) {
        fprintf(stderr, "Failed to load kernel.\n");
        exit(1);
    }

    source_str = (char*)malloc(MAX_SOURCE_SIZE);
    source_size = fread(source_str, 1, MAX_SOURCE_SIZE, fp);
    source_str[source_size] = '\0';
    fclose(fp);

    return source_str;
}

int main(int argc, char** argv) {
    if (argc != 2) {
        fprintf(stderr, "Usage: %s <kernel_file.cl>\n", argv[0]);
        return 1;
    }

    // Read kernel file
    char* kernel_source = read_kernel_file(argv[1]);
    
    // Initialize result array
    int *result = (int*)malloc(sizeof(int)*NUM_WORK_ITEMS);
    int *a = (int*)malloc(sizeof(int)*NUM_WORK_ITEMS);
    int *b = (int*)malloc(sizeof(int)*NUM_WORK_ITEMS);
    std::ifstream infile("input.txt");
    if (!infile) {
        std::cerr << "Failed to open data.txt\n";
        return 1;
    }

    for (int i = 0; i < NUM_WORK_ITEMS; ++i) {
        infile >> result[i];
    }
    // Read first 8 values into a, next 8 into b
    for (int i = 0; i < NUM_WORK_ITEMS; ++i) {
        infile >> a[i];
    }
    for (int i = 0; i < NUM_WORK_ITEMS; ++i) {
        infile >> b[i];
    }


    // Get platform and device information
    cl_platform_id platform_id = NULL;
    cl_device_id device_id = NULL;
    cl_uint ret_num_devices;
    cl_uint ret_num_platforms;
    cl_int ret = clGetPlatformIDs(1, &platform_id, &ret_num_platforms);
    ret = clGetDeviceIDs(platform_id, CL_DEVICE_TYPE_GPU, 1, &device_id, &ret_num_devices);

    // Create an OpenCL context
    cl_context context = clCreateContext(NULL, 1, &device_id, NULL, NULL, &ret);

    // Create a command queue
    cl_command_queue command_queue = clCreateCommandQueueWithProperties(context, device_id, 0, &ret);

    // Create memory buffer for result
    cl_mem result_mem_obj = clCreateBuffer(context, CL_MEM_WRITE_ONLY, NUM_WORK_ITEMS * sizeof(int), NULL, &ret);

    // Create a program from the kernel source
    cl_program program = clCreateProgramWithSource(context, 1, (const char **)&kernel_source, NULL, &ret);

    // Build the program
    ret = clBuildProgram(program, 1, &device_id, NULL, NULL, NULL);
    if (ret != CL_SUCCESS) {
        size_t log_size;
        clGetProgramBuildInfo(program, device_id, CL_PROGRAM_BUILD_LOG, 0, NULL, &log_size);
        char *log = (char *)malloc(log_size);
        clGetProgramBuildInfo(program, device_id, CL_PROGRAM_BUILD_LOG, log_size, log, NULL);
        printf("Build log:\n%s\n", log);
        free(log);
        exit(1);
    }

    // Create the OpenCL kernel
    cl_kernel kernel = clCreateKernel(program, "for_loop", &ret);
    if (ret != CL_SUCCESS) {
        fprintf(stderr, "Failed to create kernel (error: %d). Make sure the kernel name is 'for_loop'\n", ret);
        exit(1);
    }

    // Set the kernel argument
    ret = clSetKernelArg(kernel, 0, sizeof(cl_mem), (void *)&result_mem_obj);

    // Execute the OpenCL kernel with exactly 8 work-items
    size_t global_item_size = NUM_WORK_ITEMS;
    size_t local_item_size = NUM_WORK_ITEMS;
    ret = clEnqueueNDRangeKernel(command_queue, kernel, 1, NULL, &global_item_size, &local_item_size, 0, NULL, NULL);

    // Read back the results
    ret = clEnqueueReadBuffer(command_queue, result_mem_obj, CL_TRUE, 0, NUM_WORK_ITEMS * sizeof(int), result, 0, NULL, NULL);

    // Display results
    printf("Results from 8 work-items (each calculates sum from 0 to 9):\n");
    for (int i = 0; i < NUM_WORK_ITEMS; i++) {
        printf("Work-item %d result: %d\n", i, result[i]);
    }

    std::ofstream outFile("nvidia_output.txt");

    // Check if the file opened successfully
    if (outFile.is_open()) {
        for (int i = 0; i < NUM_WORK_ITEMS; ++i) {
            outFile << result[i] << " ";  // Write each element to a new line
        }
        for (int i = 0; i < NUM_WORK_ITEMS; ++i) {
            outFile << a[i] << " ";  // Write each element to a new line
        }
        for (int i = 0; i < NUM_WORK_ITEMS; ++i) {
            outFile << b[i] << " ";  // Write each element to a new line
        }

        outFile.close();  // Close the file
        std::cout << "Array written to output.txt successfully.\n";
    } else {
        std::cerr << "Unable to open file.\n";
    }



    // Verify the calculation (0+1+2+...+9 = 45)
    printf("\nExpected value for each work-item: %d\n", 45);

    // Clean up
    clFlush(command_queue);
    clFinish(command_queue);
    clReleaseKernel(kernel);
    clReleaseProgram(program);
    clReleaseMemObject(result_mem_obj);
    clReleaseCommandQueue(command_queue);
    clReleaseContext(context);
    free(result);
    free(kernel_source);

    return 0;
}