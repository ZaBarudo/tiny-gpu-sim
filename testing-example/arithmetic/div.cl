__kernel void div(__global float* a, __global float* b, __global float* result) {
    int i = get_global_id(0);
    result[i] = a[i] / b[i];
}