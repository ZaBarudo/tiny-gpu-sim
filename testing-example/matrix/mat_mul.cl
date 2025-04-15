__kernel void mat_mul(__global int* a, __global int* b, __global int* c) {
    int id = get_global_id(0);
    int width = 2;

    // Compute x and y from the flattened 1D index
    int x = id % width;
    int y = id / width;

    int sum = 0;
    for(int k = 0; k < width; k++)
        sum += a[y * width + k] * b[k * width + x];

    c[y * width + x] = sum;
}