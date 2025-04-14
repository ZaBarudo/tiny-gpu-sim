__kernel void mat_add(__global float* a, __global float* b, __global float* c, int width) {
    int x = get_global_id(0);
    int y = get_global_id(1);
    c[y*width+x] = a[y*width+x] + b[y*width+x];
}