__kernel void mat_mul(__global float* a, __global float* b, __global float* c, int width) {
    int x = get_global_id(0);
    int y = get_global_id(1);
    float sum = 0;
    for(int k=0; k<width; k++)
        sum += a[y*width+k] * b[k*width+x];
    c[y*width+x] = sum;
}