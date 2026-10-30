/* EF-02, EF-05 : conversion et plage physique — À COMPLÉTER (partie guidée G1) */
#include "unity.h"
#include "convert.h"

void setUp(void) {}
void tearDown(void) {}

void test_EF02_adc_0_gives_minus_50_00(void)         /* TC-02-01 */
{ bool v; TEST_ASSERT_EQUAL_INT32(-5000, temp_from_adc(0u, &v)); TEST_ASSERT_FALSE(v); }

void test_EF02_adc_2048_gives_115_00(void)             /* TC-02-03 : valeur médiane */
{ bool v; TEST_ASSERT_INT32_WITHIN(1, 11500, temp_from_adc(2048u, &v)); TEST_ASSERT_TRUE(v); }

void test_EF02_adc_931_gives_25_00(void)
{
    bool v;
    TEST_ASSERT_INT32_WITHIN(3, 2500, temp_from_adc(931u, &v));
    TEST_ASSERT_TRUE(v);
}


void test_EF02_adc_lower_physical_boundary(void)
{
    bool valid;
    TEST_ASSERT_EQUAL_INT32(-4001, temp_from_adc(124u, &valid));
    TEST_ASSERT_FALSE(valid);
    TEST_ASSERT_EQUAL_INT32(-3993, temp_from_adc(125u, &valid));
    TEST_ASSERT_TRUE(valid);
}

void test_EF02_adc_upper_physical_boundary(void)
{
    bool valid;
    TEST_ASSERT_EQUAL_INT32(12499, temp_from_adc(2172u, &valid));
    TEST_ASSERT_TRUE(valid);
    TEST_ASSERT_EQUAL_INT32(12507, temp_from_adc(2173u, &valid));
    TEST_ASSERT_FALSE(valid);
}

void test_EF02_adc_code_above_12_bits_is_invalid(void)
{
    bool valid = true;
    TEST_ASSERT_EQUAL_INT32(0, temp_from_adc(4096u, &valid));
    TEST_ASSERT_FALSE(valid);
}

void test_EF05_temperature_range_boundaries_are_inclusive(void)
{
    TEST_ASSERT_TRUE(range_check(-4000));
    TEST_ASSERT_FALSE(range_check(-4001));
    TEST_ASSERT_TRUE(range_check(12500));
    TEST_ASSERT_FALSE(range_check(12501));
}

int main(void)
{
    UNITY_BEGIN();
    RUN_TEST(test_EF02_adc_0_gives_minus_50_00);
    RUN_TEST(test_EF02_adc_2048_gives_115_00);
    RUN_TEST(test_EF02_adc_931_gives_25_00);
    RUN_TEST(test_EF02_adc_lower_physical_boundary);
    RUN_TEST(test_EF02_adc_upper_physical_boundary);
    RUN_TEST(test_EF02_adc_code_above_12_bits_is_invalid);
    RUN_TEST(test_EF05_temperature_range_boundaries_are_inclusive);
    return UNITY_END();
}
