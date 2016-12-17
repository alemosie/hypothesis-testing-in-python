class ChiSquareTestOfHomogeneity():
    """
    Overview
    =======================
    Run a chi-square test of homogeneity to determine whether frequency counts
    are distributed identically across different populations.

    The test should be applied to a single categorical variable from two different populations,
    where data from the categorical variable is represented in binary format.

        Example condition data format
        -----------------------
        condition="Survived"
        df["Survived"] should contain only 0s and 1s.


    Keyword arguments
    =======================
    population_labels -- labels for your comparison and expected frequency tables
    population_datasets -- data that contains observed frequencies to measure; condition column required
    condition -- the column out of the datasets provided that will be measured in the test
    alpha -- level of statistical significance
    critical_value = chi-square critical value (see notes for details)


    Other
    =======================
    Default critical value based on alpha level and 1 degree of freedom and the table:
        https://faculty.elgin.edu/dkernler/statistics/ch09/images/chi-square-table.gif
    More information about the test here:
        http://stattrek.com/chi-square-test/homogeneity.aspx?Tutorial=AP
    """

    def __init__(self, population_labels=[], population_datasets=[], condition="", alpha=0.01, critical_value=6.635):
        if len(population_labels) > 2:
            raise ValueError("Cannot compare more than two populations.")
        elif len(set(population_labels)) != len(population_labels):
            raise ValueError("Cannot compare the same population")
        else:
            self.pop1_data, self.pop2_data = population_datasets[0], population_datasets[1]
            self.pop1_label, self.pop2_label = population_labels[0], population_labels[1]
            self.condition = condition
            self.inverse_condition = "Not %s" % self.condition
            self.alpha = alpha
            self.crit = critical_value

    def calculate_condition_counts(self, pop_data):
        return pop_data[self.condition].sum(), (pop_data[self.condition].count() - pop_data[self.condition].sum())

    def generate_comp_table(self):
        '''Create comparison table'''
        pop1_condition, pop1_inverse = self.calculate_condition_counts(self.pop1_data)
        pop2_condition, pop2_inverse = self.calculate_condition_counts(self.pop2_data)
        total_condition = pop1_condition + pop2_condition
        total_inverse = pop1_inverse + pop2_inverse
        total_pop1 = self.pop1_data[self.condition].count()
        total_pop2 = self.pop2_data[self.condition].count()
        self.comp_table = pd.DataFrame({(self.condition): {self.pop1_label: pop1_condition,
                                                     self.pop2_label: pop2_condition,
                                                     "Total": total_condition},
                                        self.inverse_condition: {self.pop1_label: pop1_inverse,
                                                 self.pop2_label: pop2_inverse,
                                                 "Total": total_inverse},
                                        "Total": {self.pop1_label: total_pop1,
                                                  self.pop2_label: total_pop2,
                                                  "Total": total_pop1+total_pop2}}).T[[self.pop1_label, self.pop2_label, "Total"]].T
        print "\n\nComparison Table\n"
        print self.comp_table

    def calculate_E(self, row_total, column_total):
        grand_total = self.comp_table.loc["Total"]["Total"]
        return (row_total * column_total) / grand_total

    def calculate_E_by_pop(self, pop):
        inverse = self.calculate_E(self.comp_table.loc[pop]["Total"], self.comp_table.loc[pop][self.inverse_condition])
        condition = self.calculate_E(self.comp_table.loc[pop]["Total"], self.comp_table.loc[pop][self.condition])
        return inverse, condition

    def generate_e_table(self):
        '''Create expected frequency contingency table'''
        # helpful resource: http://www.pindling.org/Math/Statistics/Textbook/Chapter11_Chi_Square/homogeneity.html

        pop1_inverse_e, pop1_condition_e = self.calculate_E_by_pop(self.pop1_label)
        pop2_inverse_e, pop2_condition_e = self.calculate_E_by_pop(self.pop2_label)
        self.e_table =  pd.DataFrame({self.condition: {self.pop1_label: pop1_condition_e, self.pop2_label: pop2_condition_e},
                                      self.inverse_condition: {self.pop1_label: pop1_inverse_e, self.pop2_label: pop2_inverse_e}})
        print "\n\nExpected Frequency Table\n"
        print self.e_table

    def print_results(self):
        print "\n\nResults\n"
        print "Chi-square: %f" % self.chi_square
        print "Chi-square critical value at p=%f: %f" % (self.alpha, self.crit)
        print "Statistically significant: %s" % (self.chi_square > self.crit)

    def run_test(self):
        '''Run a chi-square test of homogeneity based on the population data and parameters
        with which the instance was created'''

        print "Chi-Square Test of Homogeneity"
        print "Comparison of Rates of Survival between %s and %s" % (self.pop1_label, self.pop2_label)

        # Step 0: generate tables

        self.generate_comp_table()
        self.generate_e_table()

        # Step 1: subtract observed from expected
        comp_wo_totals = self.comp_table[[self.inverse_condition, self.condition]].loc[[self.pop1_label, self.pop2_label]]
        diff = comp_wo_totals - self.e_table

        # Step 2: square each value
        diff = diff**2

        # Step 3: divide by expected frequency
        diff = diff/self.e_table

        # Step 4: calculate chi-square
        self.chi_square = diff.loc[self.pop1_label].sum() + diff.loc[self.pop2_label].sum()

        # Step 5: print results
        self.print_results()
