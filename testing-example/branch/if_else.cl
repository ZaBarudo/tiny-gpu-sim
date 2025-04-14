__kernel void if_else(__global int* a, __global int* result) {
    int i = get_global_id(0);
    result[i] = (a[i] > 0) ? 1 : 0;
}