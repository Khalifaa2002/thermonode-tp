/* EF-05 : décision de défaut (MC/DC), gel, reprise */
#include "unity.h"
#include "fault.h"

void setUp(void) { fault_reset(); }
void tearDown(void) {}

/* MC/DC : D = (A || B) || C ; A: centi<-4000, B: centi>12500, C: frozen>=5 */
void test_EF05_MCDC_T1_all_false_no_fault(void)
{ 
    TEST_ASSERT_FALSE(fault_detect(2500, 931u, true)); 
}

void test_EF05_MCDC_T2_A_true(void)
{ 
    TEST_ASSERT_TRUE(fault_detect(-4001, 124u, false)); 
}

void test_EF05_MCDC_T3_B_true(void)
{ 
    TEST_ASSERT_TRUE(fault_detect(12507, 2173u, false)); 
}

void test_EF05_MCDC_T4_C_true_frozen_five(void)
{ 
    for (int i = 0; i < 4; i++) { 
        TEST_ASSERT_FALSE(fault_detect(2500, 931u, true)); 
    }
    TEST_ASSERT_TRUE(fault_detect(2500, 931u, true)); 
    TEST_ASSERT_EQUAL_UINT32(5, fault_frozen_count()); 
}

void test_EF05_four_identical_then_different_is_not_frozen(void) /* limite 4 / 5 */
{ 
    for (int i = 0; i < 4; i++) { 
        fault_detect(2500, 931u, true); 
    } 
    TEST_ASSERT_FALSE(fault_detect(2508, 932u, true)); 
}

void test_EF05_recovery_after_five_valid(void)
{
    fault_detect(12999, 2234u, false);
    for (int i = 0; i < 4; i++) { 
        fault_detect(2500 + i * 8, (uint16_t)(931 + i), true);
        TEST_ASSERT_FALSE(fault_recover_ready()); 
    }
    fault_detect(2540, 936u, true); 
    TEST_ASSERT_TRUE(fault_recover_ready());
}

void test_EF05_invalid_in_recovery_resets_run(void)
{
    fault_detect(12999, 2234u, false);
    for (int i = 0; i < 4; i++) { 
        fault_detect(2500 + i * 8, (uint16_t)(931 + i), true); 
    }
    fault_detect(12999, 2234u, false);
    TEST_ASSERT_FALSE(fault_recover_ready());
}

void test_EF05_invalid_adc_code_is_fault(void)
{ 
    TEST_ASSERT_TRUE(fault_detect(0, 4096u, false)); 
}

int main(void)
{
    UNITY_BEGIN();
    RUN_TEST(test_EF05_MCDC_T1_all_false_no_fault);
    RUN_TEST(test_EF05_MCDC_T2_A_true);
    RUN_TEST(test_EF05_MCDC_T3_B_true);
    RUN_TEST(test_EF05_MCDC_T4_C_true_frozen_five);
    RUN_TEST(test_EF05_four_identical_then_different_is_not_frozen);
    RUN_TEST(test_EF05_recovery_after_five_valid);
    RUN_TEST(test_EF05_invalid_in_recovery_resets_run);
    RUN_TEST(test_EF05_invalid_adc_code_is_fault);
    return UNITY_END();
}