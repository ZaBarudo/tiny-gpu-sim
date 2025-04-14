__kernel void div(__global int* a, __global int* b, __global int* result) {
    int i = get_global_id(0);
    result[i] = a[i] / b[i];
}