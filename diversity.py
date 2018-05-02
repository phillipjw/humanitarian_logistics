# Compute the Heterogenity of the population
# Each diversity measure reflects the % size
# of the plurality of the population for each
# measure.

class Diversity:

    def __init__(self, list_of_azcs):
        self.azcs = list_of_azcs
        self.country_diversity = []
        self.legal_status_diversity = []
        
    def country(self, activity=False):
        most_common_countries = []
        if not activity:
            for azc in self.azcs:
                countries = []
                for newcomer in azc.occupants:
                    countries.append(newcomer.coo)
                    if (len(countries)>0):
                        most_common_country = self.most_common(countries)
                        pluralitySize = countries.count(most_common_country)
                        self.country_diversity.append(1.0-(pluralitySize/len(azc.occupants)))
        else:
            for azc in self.azcs:
                for an_activity in azc.activities_available:
                    countries = []
                    for newcomer in an_activity.participants:
                        countries.append(newcomer.coo)
                        if (len(countries)>0):
                            most_common_country = self.most_common(countries)
                            pluralitySize = countries.count(most_common_country)
                            self.country_diversity.append(1.0-(pluralitySize/len(an_activity.participants)))

        return self.country_diversity

    def legalStatus(self, activity=False):
        most_common_ls = []
        if not activity:
            for azc in self.azcs:
                legal_statuses = []
                for newcomer in azc.occupants:
                    legal_statuses.append(newcomer.ls)
                    if (len(legal_statuses)>0):
                        most_common_ls = self.most_common(legal_statuses)
                        pluralitySize = legal_statuses.count(most_common_ls)
                        self.legal_status_diversity.append(1.0-(pluralitySize/len(azc.occupants)))
                        
        else:
            for azc in self.azcs:
                for an_activity in azc.activities_available:
                    legal_statuses = []
                    for newcomer in an_activity.participants:
                        legal_statuses.append(newcomer.ls)
                        if (len(legal_statuses)>0):
                            most_common_ls = self.most_common(legal_statuses)
                            pluralitySize = legal_statuses.count(most_common_ls)
                            self.legal_status_diversity.append(1.0-(pluralitySize/len(an_activity.participants)))
        
        return self.legal_status_diversity
    def most_common(self, lst):
        return max(set(lst), key=lst.count)