__kernel void while_loop(__global int* result) {
    int i=0, sum=0;
    while(i<5) sum += i++;
    result[get_global_id(0)] = sum;
}