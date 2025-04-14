__kernel void for_loop(__global int* result) {
    int sum = 0;
    for(int i=0; i<10; i++) sum += i;
    result[get_global_id(0)] = sum;
}