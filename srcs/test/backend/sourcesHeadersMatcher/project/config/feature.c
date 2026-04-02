#define FEATURE_NAME "sourcesHeadersMatcher fixture"




const char *feature_name(void)
{
    runtime_flag_t flag = {"fixture", 1};

    (void)flag;
    return FEATURE_NAME;
}
