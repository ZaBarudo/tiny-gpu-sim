__kernel void for_loop(__global int* result) {
    int sum = 0, j = get_global_id(0);
    for(int i=0; i<10; i++) sum += i;
    result[j] = sum;
}