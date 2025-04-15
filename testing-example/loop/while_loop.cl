__kernel void while_loop(__global int* result) {
    int sum=0;
    int i=0;
    while(i<10) {
        result[get_global_id(0)] = i;
        i = i+1;
    }
}