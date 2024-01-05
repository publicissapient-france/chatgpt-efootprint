countries_list = [Countries.FRANCE, Countries.AUSTRIA, Countries.NORWAY, Countries.BELGIUM, Countries.FINLAND,
                  Countries.GERMANY, Countries.POLAND, Countries.HUNGARY, Countries.UNITED_KINGDOM]

usage_patterns = []

for country in countries_list:
    usage_pattern_name = "buying journey " + country.name
    population = DevicePopulation(
        f"Sonepar customers in {country.name}", SourceValue(617307 * u.user), country, devices=[Devices.LAPTOP])
    usage_pattern = UsagePattern(
        usage_pattern_name, user_journey, population, Networks.WIFI_NETWORK,
        user_journey_freq_per_user=SourceValue(
            1 * u.user_journey / (u.user * u.year)), time_intervals=SourceObject([[8, 16]]))
    usage_patterns.append(usage_pattern)