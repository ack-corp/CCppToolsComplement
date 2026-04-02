#include <stdio.h>


int main(void)
{
    int total = compute_total(20, 22);

    log_result(total);
    printf("%s\n", feature_name());
    return 0;
}
