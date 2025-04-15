__kernel void mat_add(__global int* a, __global int* b, __global int* c) {
    int gid = get_global_id(0);
    int width = 2;
    int x = gid % width;
    int y = gid / width;

    if (x < width && y < width) {
        int index = y * width + x;
        c[index] = a[index] + b[index];
    }
}