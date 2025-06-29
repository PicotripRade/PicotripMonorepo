def get_weights(dataframe, activity_tag='None'):

    if activity_tag == 'summer_vacation':
        weights = {'origin airport': 0,
                   'trip duration': 0,
                   'index': 0,
                   'airport': 1,
                   'city': 0,
                   'distance from origin': 0,
                   'airport coor': 0,
                   'city coor': 0,
                   'airport country': 0,
                   'city country': 0,
                   'city population': 0,
                   'distance from airport': 0,
                   'Meal, Inexpensive Restaurant (USD)': 0,
                   'Meal for 2 People, Mid-range Restaurant, Three-course (USD)': 0,
                   'McMeal at McDonalds (or Equivalent Combo Meal) (USD)': 0,
                   'Domestic Beer (0.5 liter draught, in restaurants) (USD)': 0,
                   'Imported Beer (0.33 liter bottle, in restaurants) (USD)': 0,
                   'Cappuccino (regular, in restaurants) (USD)': 0,
                   'Coke/Pepsi (0.33 liter bottle, in restaurants) (USD)': 0,
                   'Water (0.33 liter bottle, in restaurants) (USD)': 0,
                   'Milk (regular), (1 liter) (USD)': 0,
                   'Loaf of Fresh White Bread (500g) (USD)': 0,
                   'Rice (white), (1kg) (USD)': 0,
                   'Eggs (regular) (12) (USD)': 0,
                   'Local Cheese (1kg) (USD)': 0,
                   'Chicken Fillets (1kg) (USD)': 0,
                   'Beef Round (1kg) (or Equivalent Back Leg Red Meat) (USD)': 0,
                   'Apples (1kg) (USD)': 0,
                   'Banana (1kg) (USD)': 0,
                   'Oranges (1kg) (USD)': 0,
                   'Tomato (1kg) (USD)': 0,
                   'Potato (1kg) (USD)': 0,
                   'Onion (1kg) (USD)': 0,
                   'Lettuce (1 head) (USD)': 0,
                   'Water (1.5 liter bottle, at the market) (USD)': 0,
                   'Bottle of Wine (Mid-Range, at the market) (USD)': 0,
                   'Domestic Beer (0.5 liter bottle, at the market) (USD)': 0,
                   'Imported Beer (0.33 liter bottle, at the market) (USD)': 0,
                   'Cigarettes 20 Pack (Marlboro) (USD)': 0,
                   'One-way Ticket (Local Transport) (USD)': 0,
                   'Monthly Pass (Regular Price) (USD)': 0,
                   'Taxi Start (Normal Tariff) (USD)': 0,
                   'Taxi 1km (Normal Tariff) (USD)': 0,
                   'Taxi 1hour Waiting (Normal Tariff) (USD)': 0,
                   'Gasoline (1 liter) (USD)': 0,
                   'Volkswagen Golf 1.4 90 KW Trendline (Or Equivalent New Car) (USD)': 0,
                   'Toyota Corolla Sedan 1.6l 97kW Comfort (Or Equivalent New Car) (USD)': 0,
                   'Basic (Electricity, Heating, Cooling, Water, Garbage) for 85m2 Apartment (USD)': 0,
                   '1 min. of Prepaid Mobile Tariff Local (No Discounts or Plans) (USD)': 0,
                   'Internet (60 Mbps or More, Unlimited Data, Cable/ADSL) (USD)': 0,
                   'Fitness Club, Monthly Fee for 1 Adult (USD)': 0,
                   'Tennis Court Rent (1 Hour on Weekend) (USD)': 0,
                   'Cinema, International Release, 1 Seat (USD)': 0,
                   'Preschool (or Kindergarten), Full Day, Private, Monthly for 1 Child (USD)': 0,
                   'International Primary School, Yearly for 1 Child (USD)': 0,
                   '1 Pair of Jeans (Levis 501 Or Similar) (USD)': 0,
                   '1 Summer Dress in a Chain Store (Zara, H&M, …) (USD)': 0,
                   '1 Pair of Nike Running Shoes (Mid-Range) (USD)': 0,
                   '1 Pair of Men Leather Business Shoes (USD)': 0,
                   'Apartment (1 bedroom) in City Centre (USD)': 0,
                   'Apartment (1 bedroom) Outside of Centre (USD)': 0,
                   'Apartment (3 bedrooms) in City Centre (USD)': 0,
                   'Apartment (3 bedrooms) Outside of Centre (USD)': 0,
                   'Price per Square Meter to Buy Apartment in City Centre (USD)': 0,
                   'Price per Square Meter to Buy Apartment Outside of Centre (USD)': 0,
                   'Average Monthly Net Salary (After Tax) (USD)': 0,
                   'Mortgage Interest Rate in Percentages (%), Yearly, for 20 Years Fixed-Rate': 0,
                   '0 if Numbeo considers that more contributors are needed to increase data quality, else 1': 0,
                   'ANCH': 0,
                   'bay': 5,
                   'bays': 5,
                   'icecap': 0,
                   'channel': 0,
                   'cove(s)': 0,
                   'icecap dome': 0,
                   'icecap depression': 0,
                   'fishing area': 5,
                   'fjord': 0,
                   'fjords': 0,
                   'waterfall(s)': 0,
                   'section of waterfall(s)': 0,
                   'glacier(s)': 0,
                   'gulf': 0,
                   'geyser': 0,
                   'lagoon': 5,
                   'lagoons': 5,
                   'section of lagoon': 5,
                   'lake': 0,
                   'crater lake': 0,
                   'intermittent lake': 0,
                   'salt lake': 0,
                   'intermittent salt lake': 0,
                   'oxbow lake': 0,
                   'intermittent oxbow lake': 0,
                   'lakes': 0,
                   'crater lakes': 0,
                   'intermittent lakes': 0,
                   'salt lakes': 0,
                   'intermittent salt lakes': 0,
                   'section of lake': 0,
                   'ocean': 5,
                   'overfalls': 0,
                   'icecap ridge': 0,
                   'coral reef(s)': 5,
                   'sea': 10,
                   'spring(s)': 0,
                   'hot spring(s)': 0,
                   'lost river': 0,
                   'section of stream': 0,
                   'strait': 0,
                   'swamp': 0,
                   'wadi': 0,
                   'amusement park': 0,
                   'battlefield': 0,
                   'coast': 10,
                   'business center': 0,
                   'arctic land': 0,
                   'oasis(-es)': 0,
                   'park': 0,
                   'forest reserve': 0,
                   'hunting reserve': 0,
                   'nature reserve': 0,
                   'palm tree reserve': 30,
                   'wildlife reserve':200,
                   'historical region': 0,
                   'lake region': 0,
                   'snowfield': 0,
                   'capital of a political entity': 0,
                   'historical capital of a political entity': 0,
                   'historical populated place': 0,
                   'religious populated place': 0,
                   'promenade': 5,
                   'portage': 0,
                   'ancient road': 0,
                   'natural tunnel': 0,
                   'piece of art': 0,
                   'cave(s)': 0,
                   'camp(s)': 5,
                   'logging camp': 0,
                   'corral(s)': 0,
                   'casino': 0,
                   'castle': 0,
                   'garden(s)': 30,
                   'guest house': 59,
                   'historical site': 0,
                   'hotel': 10,
                   'mall': 0,
                   'marina': 10,
                   'market': 0,
                   'monument': 0,
                   'mosque': 0,
                   'monastery': 0,
                   'museum': 0,
                   'observation point': 0,
                   'opera house': 0,
                   'palace': 0,
                   'pyramid': 0,
                   'pyramids': 0,
                   'golf course': 10,
                   'racetrack': 0,
                   'restaurant': 0,
                   'store': 0,
                   'resthouse': 0,
                   'religious site': 0,
                   'resort': 10,
                   'spa': 5,
                   'square': 0,
                   'stadium': 0,
                   'synagogue': 0,
                   'theater': 0,
                   'temple(s)': 0,
                   'atoll(s)': 0,
                   'beach': 100,
                   'beaches': 100,
                   'blowhole(s)': 0,
                   'cape': 0,
                   'cleft(s)': 0,
                   'cliff(s)': 0,
                   'canyon': 0,
                   'cone(s)': 0,
                   'cirque': 0,
                   'cirques': 0,
                   'crater(s)': 0,
                   'desert': 0,
                   'dune(s)': 0,
                   'sandy desert': 0,
                   'ford': 0,
                   'rock desert': 0,
                   'island': 50,
                   'islet': 0,
                   'artificial island': 0,
                   'mangrove island': 0,
                   'islands': 10,
                   'land-tied island': 0,
                   'section of island': 100,
                   'mound(s)': 0,
                   'moraine': 0,
                   'mountain': 0,
                   'mountains': 0,
                   'nunatak': 0,
                   'nunataks': 0,
                   'peninsula': 5,
                   'section of peninsula': 0,
                   'peak': 0,
                   'peaks': 0,
                   'section of plateau': 0,
                   'beach ridge': 5,
                   'terrace': 0,
                   'volcano': 0,
                   'borderland': 0,
                   'banks': 0,
                   'bank': 0,
                   'basin': 0,
                   'continental rise': 0,
                   'deep': 5,
                   'fan': 0,
                   'gap': 0,
                   'gully': 0,
                   'hill': 0,
                   'hills': 0,
                   'knoll': 0,
                   'knolls': 0,
                   'levee': 0,
                   'mound': 0,
                   'moat': 0,
                   'underwater mountain': 5,
                   'province': 0,
                   'ridge': 0,
                   'ridges': 0,
                   'reefs': 5,
                   'reef': 5,
                   'rise': 0,
                   'seachannel': 0,
                   'seachannels': 0,
                   'saddle': 0,
                   'shelf': 0,
                   'tablemounts (or guyots)': 0,
                   'tablemount (or guyot)': 0,
                   'trough': 0,
                   'trench': 5,
                   'valley': 0,
                   'valleys': 0,
                   'bush(es)': 0,
                   'cultivated area': 0,
                   'grove': 0,
                   'grassland': 0,
                   'vineyard': 0,
                   'vineyards': 0}
    elif activity_tag == 'mountain_bike':
        weights = {'origin airport': 0,
                   'trip duration': 0,
                   'index': 0,
                   'airport': 1,
                   'city': 0,
                   'distance from origin': 2,
                   'airport coor': 0,
                   'city coor': 0,
                   'airport country': 0,
                   'city country': 0,
                   'city population': 8,
                   'distance from airport': 0,
                   'Meal, Inexpensive Restaurant (USD)': 0,
                   'Meal for 2 People, Mid-range Restaurant, Three-course (USD)': 0,
                   'McMeal at McDonalds (or Equivalent Combo Meal) (USD)': 0,
                   'Domestic Beer (0.5 liter draught, in restaurants) (USD)': 0,
                   'Imported Beer (0.33 liter bottle, in restaurants) (USD)': 0,
                   'Cappuccino (regular, in restaurants) (USD)': 0,
                   'Coke/Pepsi (0.33 liter bottle, in restaurants) (USD)': 0,
                   'Water (0.33 liter bottle, in restaurants) (USD)': 0,
                   'Milk (regular), (1 liter) (USD)': 0,
                   'Loaf of Fresh White Bread (500g) (USD)': 0,
                   'Rice (white), (1kg) (USD)': 0,
                   'Eggs (regular) (12) (USD)': 0,
                   'Local Cheese (1kg) (USD)': 0,
                   'Chicken Fillets (1kg) (USD)': 0,
                   'Beef Round (1kg) (or Equivalent Back Leg Red Meat) (USD)': 0,
                   'Apples (1kg) (USD)': 0,
                   'Banana (1kg) (USD)': 0,
                   'Oranges (1kg) (USD)': 0,
                   'Tomato (1kg) (USD)': 0,
                   'Potato (1kg) (USD)': 0,
                   'Onion (1kg) (USD)': 0,
                   'Lettuce (1 head) (USD)': 0,
                   'Water (1.5 liter bottle, at the market) (USD)': 0,
                   'Bottle of Wine (Mid-Range, at the market) (USD)': 0,
                   'Domestic Beer (0.5 liter bottle, at the market) (USD)': 0,
                   'Imported Beer (0.33 liter bottle, at the market) (USD)': 0,
                   'Cigarettes 20 Pack (Marlboro) (USD)': 0,
                   'One-way Ticket (Local Transport) (USD)': 0,
                   'Monthly Pass (Regular Price) (USD)': 0,
                   'Taxi Start (Normal Tariff) (USD)': 0,
                   'Taxi 1km (Normal Tariff) (USD)': 0,
                   'Taxi 1hour Waiting (Normal Tariff) (USD)': 0,
                   'Gasoline (1 liter) (USD)': 0,
                   'Volkswagen Golf 1.4 90 KW Trendline (Or Equivalent New Car) (USD)': 0,
                   'Toyota Corolla Sedan 1.6l 97kW Comfort (Or Equivalent New Car) (USD)': 0,
                   'Basic (Electricity, Heating, Cooling, Water, Garbage) for 85m2 Apartment (USD)': 0,
                   '1 min. of Prepaid Mobile Tariff Local (No Discounts or Plans) (USD)': 0,
                   'Internet (60 Mbps or More, Unlimited Data, Cable/ADSL) (USD)': 0,
                   'Fitness Club, Monthly Fee for 1 Adult (USD)': 0,
                   'Tennis Court Rent (1 Hour on Weekend) (USD)': 0,
                   'Cinema, International Release, 1 Seat (USD)': 0,
                   'Preschool (or Kindergarten), Full Day, Private, Monthly for 1 Child (USD)': 0,
                   'International Primary School, Yearly for 1 Child (USD)': 0,
                   '1 Pair of Jeans (Levis 501 Or Similar) (USD)': 0,
                   '1 Summer Dress in a Chain Store (Zara, H&M, …) (USD)': 0,
                   '1 Pair of Nike Running Shoes (Mid-Range) (USD)': 0,
                   '1 Pair of Men Leather Business Shoes (USD)': 0,
                   'Apartment (1 bedroom) in City Centre (USD)': 0,
                   'Apartment (1 bedroom) Outside of Centre (USD)': 0,
                   'Apartment (3 bedrooms) in City Centre (USD)': 0,
                   'Apartment (3 bedrooms) Outside of Centre (USD)': 0,
                   'Price per Square Meter to Buy Apartment in City Centre (USD)': 0,
                   'Price per Square Meter to Buy Apartment Outside of Centre (USD)': 0,
                   'Average Monthly Net Salary (After Tax) (USD)': 0,
                   'Mortgage Interest Rate in Percentages (%), Yearly, for 20 Years Fixed-Rate': 0,
                   '0 if Numbeo considers that more contributors are needed to increase data quality, else 1': 0,
                   'ANCH': 0,
                   'bay': 0,
                   'bays': 0,
                   'icecap': 0,
                   'channel': 0,
                   'cove(s)': 0,
                   'icecap dome': 0,
                   'icecap depression': 0,
                   'fishing area': 0,
                   'fjord': 0,
                   'fjords': 0,
                   'waterfall(s)': 0,
                   'section of waterfall(s)': 0,
                   'glacier(s)': 0,
                   'gulf': 0,
                   'geyser': 0,
                   'lagoon': 0,
                   'lagoons': 0,
                   'section of lagoon': 0,
                   'lake': 0,
                   'crater lake': 0,
                   'intermittent lake': 0,
                   'salt lake': 0,
                   'intermittent salt lake': 0,
                   'oxbow lake': 0,
                   'intermittent oxbow lake': 0,
                   'lakes': 0,
                   'crater lakes': 0,
                   'intermittent lakes': 0,
                   'salt lakes': 0,
                   'intermittent salt lakes': 0,
                   'section of lake': 0,
                   'ocean': 0,
                   'overfalls': 0,
                   'icecap ridge': 0,
                   'coral reef(s)': 0,
                   'sea': 0,
                   'spring(s)': 0,
                   'hot spring(s)': 0,
                   'lost river': 0,
                   'section of stream': 0,
                   'strait': 0,
                   'swamp': 0,
                   'wadi': 0,
                   'amusement park': 0,
                   'battlefield': 0,
                   'coast': 0,
                   'business center': 0,
                   'arctic land': 0,
                   'oasis(-es)': 0,
                   'park': 0,
                   'forest reserve': 0,
                   'hunting reserve': 0,
                   'nature reserve': 0,
                   'palm tree reserve': 0,
                   'wildlife reserve': 0,
                   'historical region': 0,
                   'lake region': 0,
                   'snowfield': 0,
                   'capital of a political entity': 0,
                   'historical capital of a political entity': 0,
                   'historical populated place': 0,
                   'religious populated place': 0,
                   'promenade': 0,
                   'portage': 0,
                   'ancient road': 0,
                   'natural tunnel': 0,
                   'piece of art': 0,
                   'cave(s)': 0,
                   'camp(s)': 0,
                   'logging camp': 0,
                   'corral(s)': 0,
                   'casino': 0,
                   'castle': 0,
                   'garden(s)': 0,
                   'guest house': 0,
                   'historical site': 0,
                   'hotel': 0,
                   'mall': 0,
                   'marina': 0,
                   'market': 0,
                   'monument': 0,
                   'mosque': 0,
                   'monastery': 0,
                   'museum': 0,
                   'observation point': 0,
                   'opera house': 0,
                   'palace': 0,
                   'pyramid': 0,
                   'pyramids': 0,
                   'golf course': 0,
                   'racetrack': 0,
                   'restaurant': 0,
                   'store': 0,
                   'resthouse': 0,
                   'religious site': 0,
                   'resort': 0,
                   'spa': 0,
                   'square': 0,
                   'stadium': 0,
                   'synagogue': 0,
                   'theater': 0,
                   'temple(s)': 0,
                   'atoll(s)': 0,
                   'beach': 0,
                   'beaches': 0,
                   'blowhole(s)': 0,
                   'cape': 0,
                   'cleft(s)': 0,
                   'cliff(s)': 0,
                   'canyon': 0,
                   'cone(s)': 0,
                   'cirque': 0,
                   'cirques': 0,
                   'crater(s)': 0,
                   'desert': 0,
                   'dune(s)': 0,
                   'sandy desert': 0,
                   'ford': 0,
                   'rock desert': 0,
                   'island': 0,
                   'islet': 0,
                   'artificial island': 0,
                   'mangrove island': 0,
                   'islands': 0,
                   'land-tied island': 0,
                   'section of island': 0,
                   'mound(s)': 0,
                   'moraine': 0,
                   'mountain': 0,
                   'mountains': 0,
                   'nunatak': 0,
                   'nunataks': 0,
                   'peninsula': 0,
                   'section of peninsula': 0,
                   'peak': 0,
                   'peaks': 0,
                   'section of plateau': 0,
                   'beach ridge': 0,
                   'terrace': 0,
                   'volcano': 0,
                   'borderland': 0,
                   'banks': 0,
                   'bank': 0,
                   'basin': 0,
                   'continental rise': 0,
                   'deep': 0,
                   'fan': 0,
                   'gap': 0,
                   'gully': 0,
                   'hill': 0,
                   'hills': 0,
                   'knoll': 0,
                   'knolls': 0,
                   'levee': 0,
                   'mound': 0,
                   'moat': 0,
                   'underwater mountain': 0,
                   'province': 0,
                   'ridge': 0,
                   'ridges': 0,
                   'reefs': 0,
                   'reef': 0,
                   'rise': 0,
                   'seachannel': 0,
                   'seachannels': 0,
                   'saddle': 0,
                   'shelf': 0,
                   'tablemounts (or guyots)': 0,
                   'tablemount (or guyot)': 0,
                   'trough': 0,
                   'trench': 0,
                   'valley': 0,
                   'valleys': 0,
                   'bush(es)': 0,
                   'cultivated area': 0,
                   'grove': 0,
                   'grassland': 0,
                   'vineyard': 0,
                   'vineyards': 0}
    else:
        weights = {'origin airport': 0,
                   'trip duration': 0,
                   'index': 0,
                   'airport': 1,
                   'city': 0,
                   'distance from origin': 0,
                   'airport coor': 0,
                   'city coor': 0,
                   'airport country': 0,
                   'city country': 0,
                   'city population': 0,
                   'distance from airport': 0,
                   'Meal, Inexpensive Restaurant (USD)': 0,
                   'Meal for 2 People, Mid-range Restaurant, Three-course (USD)': 0,
                   'McMeal at McDonalds (or Equivalent Combo Meal) (USD)': 0,
                   'Domestic Beer (0.5 liter draught, in restaurants) (USD)': 0,
                   'Imported Beer (0.33 liter bottle, in restaurants) (USD)': 0,
                   'Cappuccino (regular, in restaurants) (USD)': 0,
                   'Coke/Pepsi (0.33 liter bottle, in restaurants) (USD)': 0,
                   'Water (0.33 liter bottle, in restaurants) (USD)': 0,
                   'Milk (regular), (1 liter) (USD)': 0,
                   'Loaf of Fresh White Bread (500g) (USD)': 0,
                   'Rice (white), (1kg) (USD)': 0,
                   'Eggs (regular) (12) (USD)': 0,
                   'Local Cheese (1kg) (USD)': 0,
                   'Chicken Fillets (1kg) (USD)': 0,
                   'Beef Round (1kg) (or Equivalent Back Leg Red Meat) (USD)': 0,
                   'Apples (1kg) (USD)': 0,
                   'Banana (1kg) (USD)': 0,
                   'Oranges (1kg) (USD)': 0,
                   'Tomato (1kg) (USD)': 0,
                   'Potato (1kg) (USD)': 0,
                   'Onion (1kg) (USD)': 0,
                   'Lettuce (1 head) (USD)': 0,
                   'Water (1.5 liter bottle, at the market) (USD)': 0,
                   'Bottle of Wine (Mid-Range, at the market) (USD)': 0,
                   'Domestic Beer (0.5 liter bottle, at the market) (USD)': 0,
                   'Imported Beer (0.33 liter bottle, at the market) (USD)': 0,
                   'Cigarettes 20 Pack (Marlboro) (USD)': 0,
                   'One-way Ticket (Local Transport) (USD)': 0,
                   'Monthly Pass (Regular Price) (USD)': 0,
                   'Taxi Start (Normal Tariff) (USD)': 0,
                   'Taxi 1km (Normal Tariff) (USD)': 0,
                   'Taxi 1hour Waiting (Normal Tariff) (USD)': 0,
                   'Gasoline (1 liter) (USD)': 0,
                   'Volkswagen Golf 1.4 90 KW Trendline (Or Equivalent New Car) (USD)': 0,
                   'Toyota Corolla Sedan 1.6l 97kW Comfort (Or Equivalent New Car) (USD)': 0,
                   'Basic (Electricity, Heating, Cooling, Water, Garbage) for 85m2 Apartment (USD)': 0,
                   '1 min. of Prepaid Mobile Tariff Local (No Discounts or Plans) (USD)': 0,
                   'Internet (60 Mbps or More, Unlimited Data, Cable/ADSL) (USD)': 0,
                   'Fitness Club, Monthly Fee for 1 Adult (USD)': 0,
                   'Tennis Court Rent (1 Hour on Weekend) (USD)': 0,
                   'Cinema, International Release, 1 Seat (USD)': 0,
                   'Preschool (or Kindergarten), Full Day, Private, Monthly for 1 Child (USD)': 0,
                   'International Primary School, Yearly for 1 Child (USD)': 0,
                   '1 Pair of Jeans (Levis 501 Or Similar) (USD)': 0,
                   '1 Summer Dress in a Chain Store (Zara, H&M, …) (USD)': 0,
                   '1 Pair of Nike Running Shoes (Mid-Range) (USD)': 0,
                   '1 Pair of Men Leather Business Shoes (USD)': 0,
                   'Apartment (1 bedroom) in City Centre (USD)': 0,
                   'Apartment (1 bedroom) Outside of Centre (USD)': 0,
                   'Apartment (3 bedrooms) in City Centre (USD)': 0,
                   'Apartment (3 bedrooms) Outside of Centre (USD)': 0,
                   'Price per Square Meter to Buy Apartment in City Centre (USD)': 0,
                   'Price per Square Meter to Buy Apartment Outside of Centre (USD)': 0,
                   'Average Monthly Net Salary (After Tax) (USD)': 0,
                   'Mortgage Interest Rate in Percentages (%), Yearly, for 20 Years Fixed-Rate': 0,
                   '0 if Numbeo considers that more contributors are needed to increase data quality, else 1': 0,
                   'ANCH': 0,
                   'bay': 5,
                   'bays': 5,
                   'icecap': 0,
                   'channel': 0,
                   'cove(s)': 0,
                   'icecap dome': 0,
                   'icecap depression': 0,
                   'fishing area': 5,
                   'fjord': 0,
                   'fjords': 0,
                   'waterfall(s)': 0,
                   'section of waterfall(s)': 0,
                   'glacier(s)': 0,
                   'gulf': 0,
                   'geyser': 0,
                   'lagoon': 5,
                   'lagoons': 5,
                   'section of lagoon': 5,
                   'lake': 0,
                   'crater lake': 0,
                   'intermittent lake': 0,
                   'salt lake': 0,
                   'intermittent salt lake': 0,
                   'oxbow lake': 0,
                   'intermittent oxbow lake': 0,
                   'lakes': 0,
                   'crater lakes': 0,
                   'intermittent lakes': 0,
                   'salt lakes': 0,
                   'intermittent salt lakes': 0,
                   'section of lake': 0,
                   'ocean': 5,
                   'overfalls': 0,
                   'icecap ridge': 0,
                   'coral reef(s)': 5,
                   'sea': 10,
                   'spring(s)': 0,
                   'hot spring(s)': 0,
                   'lost river': 0,
                   'section of stream': 0,
                   'strait': 0,
                   'swamp': 0,
                   'wadi': 0,
                   'amusement park': 0,
                   'battlefield': 0,
                   'coast': 5,
                   'business center': 0,
                   'arctic land': 0,
                   'oasis(-es)': 0,
                   'park': 0,
                   'forest reserve': 0,
                   'hunting reserve': 0,
                   'nature reserve': 0,
                   'palm tree reserve': 5,
                   'wildlife reserve': 2,
                   'historical region': 0,
                   'lake region': 0,
                   'snowfield': 0,
                   'capital of a political entity': 0,
                   'historical capital of a political entity': 0,
                   'historical populated place': 0,
                   'religious populated place': 0,
                   'promenade': 5,
                   'portage': 0,
                   'ancient road': 0,
                   'natural tunnel': 0,
                   'piece of art': 0,
                   'cave(s)': 0,
                   'camp(s)': 5,
                   'logging camp': 0,
                   'corral(s)': 0,
                   'casino': 0,
                   'castle': 0,
                   'garden(s)': 5,
                   'guest house': 5,
                   'historical site': 0,
                   'hotel': 10,
                   'mall': 0,
                   'marina': 10,
                   'market': 0,
                   'monument': 0,
                   'mosque': 0,
                   'monastery': 0,
                   'museum': 0,
                   'observation point': 0,
                   'opera house': 0,
                   'palace': 0,
                   'pyramid': 0,
                   'pyramids': 0,
                   'golf course': 5,
                   'racetrack': 0,
                   'restaurant': 0,
                   'store': 0,
                   'resthouse': 0,
                   'religious site': 0,
                   'resort': 10,
                   'spa': 5,
                   'square': 0,
                   'stadium': 0,
                   'synagogue': 0,
                   'theater': 0,
                   'temple(s)': 0,
                   'atoll(s)': 0,
                   'beach': 20,
                   'beaches': 20,
                   'blowhole(s)': 0,
                   'cape': 0,
                   'cleft(s)': 0,
                   'cliff(s)': 0,
                   'canyon': 0,
                   'cone(s)': 0,
                   'cirque': 0,
                   'cirques': 0,
                   'crater(s)': 0,
                   'desert': 0,
                   'dune(s)': 0,
                   'sandy desert': 0,
                   'ford': 0,
                   'rock desert': 0,
                   'island': 15,
                   'islet': 0,
                   'artificial island': 0,
                   'mangrove island': 0,
                   'islands': 10,
                   'land-tied island': 0,
                   'section of island': 10,
                   'mound(s)': 0,
                   'moraine': 0,
                   'mountain': 0,
                   'mountains': 0,
                   'nunatak': 0,
                   'nunataks': 0,
                   'peninsula': 5,
                   'section of peninsula': 0,
                   'peak': 0,
                   'peaks': 0,
                   'section of plateau': 0,
                   'beach ridge': 5,
                   'terrace': 0,
                   'volcano': 0,
                   'borderland': 0,
                   'banks': 0,
                   'bank': 0,
                   'basin': 0,
                   'continental rise': 0,
                   'deep': 5,
                   'fan': 0,
                   'gap': 0,
                   'gully': 0,
                   'hill': 0,
                   'hills': 0,
                   'knoll': 0,
                   'knolls': 0,
                   'levee': 0,
                   'mound': 0,
                   'moat': 0,
                   'underwater mountain': 5,
                   'province': 0,
                   'ridge': 0,
                   'ridges': 0,
                   'reefs': 5,
                   'reef': 5,
                   'rise': 0,
                   'seachannel': 5,
                   'seachannels': 5,
                   'saddle': 0,
                   'shelf': 0,
                   'tablemounts (or guyots)': 0,
                   'tablemount (or guyot)': 0,
                   'trough': 0,
                   'trench': 5,
                   'valley': 0,
                   'valleys': 0,
                   'bush(es)': 0,
                   'cultivated area': 0,
                   'grove': 0,
                   'grassland': 0,
                   'vineyard': 0,
                   'vineyards': 0}
    weighted_df = dataframe.mul(weights, axis=1)

    return weighted_df


def min_max_scaling_hb(column):
    return (column - column.mean()) / (column.std())
def min_max_scaling_lb(column):
    return -(column - column.mean()) / (column.std())

hb_columns = ['city population',
 'ANCH',
 'bay',
 'bays',
 'icecap',
 'channel',
 'cove(s)',
 'icecap dome',
 'icecap depression',
 'fishing area',
 'fjord',
 'fjords',
 'waterfall(s)',
 'section of waterfall(s)',
 'glacier(s)',
 'gulf',
 'geyser',
 'lagoon',
 'lagoons',
 'section of lagoon',
 'lake',
 'crater lake',
 'intermittent lake',
 'salt lake',
 'intermittent salt lake',
 'oxbow lake',
 'intermittent oxbow lake',
 'lakes',
 'crater lakes',
 'intermittent lakes',
 'salt lakes',
 'intermittent salt lakes',
 'section of lake',
 'ocean',
 'overfalls',
 'icecap ridge',
 'coral reef(s)',
 'sea',
 'spring(s)',
 'hot spring(s)',
 'lost river',
 'section of stream',
 'strait',
 'swamp',
 'wadi',
 'amusement park',
 'battlefield',
 'coast',
 'business center',
 'arctic land',
 'oasis(-es)',
 'park',
 'forest reserve',
 'hunting reserve',
 'nature reserve',
 'palm tree reserve',
 'wildlife reserve',
 'historical region',
 'lake region',
 'snowfield',
 'capital of a political entity',
 'historical capital of a political entity',
 'historical populated place',
 'religious populated place',
 'promenade',
 'portage',
 'ancient road',
 'natural tunnel',
 'piece of art',
 'cave(s)',
 'camp(s)',
 'logging camp',
 'corral(s)',
 'casino',
 'castle',
 'garden(s)',
 'guest house',
 'historical site',
 'hotel',
 'mall',
 'marina',
 'market',
 'monument',
 'mosque',
 'monastery',
 'museum',
 'observation point',
 'opera house',
 'palace',
 'pyramid',
 'pyramids',
 'golf course',
 'racetrack',
 'restaurant',
 'store',
 'resthouse',
 'religious site',
 'resort',
 'spa',
 'square',
 'stadium',
 'synagogue',
 'theater',
 'temple(s)',
 'atoll(s)',
 'beach',
 'beaches',
 'blowhole(s)',
 'cape',
 'cleft(s)',
 'cliff(s)',
 'canyon',
 'cone(s)',
 'cirque',
 'cirques',
 'crater(s)',
 'desert',
 'dune(s)',
 'sandy desert',
 'ford',
 'rock desert',
 'island',
 'islet',
 'artificial island',
 'mangrove island',
 'islands',
 'land-tied island',
 'section of island',
 'mound(s)',
 'moraine',
 'mountain',
 'mountains',
 'nunatak',
 'nunataks',
 'peninsula',
 'section of peninsula',
 'peak',
 'peaks',
 'section of plateau',
 'beach ridge',
 'terrace',
 'volcano',
 'borderland',
 'banks',
 'bank',
 'basin',
 'continental rise',
 'deep',
 'fan',
 'gap',
 'gully',
 'hill',
 'hills',
 'knoll',
 'knolls',
 'levee',
 'mound',
 'moat',
 'underwater mountain',
 'province',
 'ridge',
 'ridges',
 'reefs',
 'reef',
 'rise',
 'seachannel',
 'seachannels',
 'saddle',
 'shelf',
 'tablemounts (or guyots)',
 'tablemount (or guyot)',
 'trough',
 'trench',
 'valley',
 'valleys',
 'bush(es)',
 'cultivated area',
 'grove',
 'grassland',
 'vineyard',
 'vineyards']
lb_columns = ['distance from origin','distance from airport','Meal, Inexpensive Restaurant (USD)',
 'Meal for 2 People, Mid-range Restaurant, Three-course (USD)',
 'McMeal at McDonalds (or Equivalent Combo Meal) (USD)',
 'Domestic Beer (0.5 liter draught, in restaurants) (USD)',
 'Imported Beer (0.33 liter bottle, in restaurants) (USD)',
 'Cappuccino (regular, in restaurants) (USD)',
 'Coke/Pepsi (0.33 liter bottle, in restaurants) (USD)',
 'Water (0.33 liter bottle, in restaurants) (USD)',
 'Milk (regular), (1 liter) (USD)',
 'Loaf of Fresh White Bread (500g) (USD)',
 'Rice (white), (1kg) (USD)',
 'Eggs (regular) (12) (USD)',
 'Local Cheese (1kg) (USD)',
 'Chicken Fillets (1kg) (USD)',
 'Beef Round (1kg) (or Equivalent Back Leg Red Meat) (USD)',
 'Apples (1kg) (USD)',
 'Banana (1kg) (USD)',
 'Oranges (1kg) (USD)',
 'Tomato (1kg) (USD)',
 'Potato (1kg) (USD)',
 'Onion (1kg) (USD)',
 'Lettuce (1 head) (USD)',
 'Water (1.5 liter bottle, at the market) (USD)',
 'Bottle of Wine (Mid-Range, at the market) (USD)',
 'Domestic Beer (0.5 liter bottle, at the market) (USD)',
 'Imported Beer (0.33 liter bottle, at the market) (USD)',
 'Cigarettes 20 Pack (Marlboro) (USD)',
 'One-way Ticket (Local Transport) (USD)',
 'Monthly Pass (Regular Price) (USD)',
 'Taxi Start (Normal Tariff) (USD)',
 'Taxi 1km (Normal Tariff) (USD)',
 'Taxi 1hour Waiting (Normal Tariff) (USD)',
 'Gasoline (1 liter) (USD)',
 'Volkswagen Golf 1.4 90 KW Trendline (Or Equivalent New Car) (USD)',
 'Toyota Corolla Sedan 1.6l 97kW Comfort (Or Equivalent New Car) (USD)',
 'Basic (Electricity, Heating, Cooling, Water, Garbage) for 85m2 Apartment (USD)',
 '1 min. of Prepaid Mobile Tariff Local (No Discounts or Plans) (USD)',
 'Internet (60 Mbps or More, Unlimited Data, Cable/ADSL) (USD)',
 'Fitness Club, Monthly Fee for 1 Adult (USD)',
 'Tennis Court Rent (1 Hour on Weekend) (USD)',
 'Cinema, International Release, 1 Seat (USD)',
 'Preschool (or Kindergarten), Full Day, Private, Monthly for 1 Child (USD)',
 'International Primary School, Yearly for 1 Child (USD)',
 '1 Pair of Jeans (Levis 501 Or Similar) (USD)',
 '1 Summer Dress in a Chain Store (Zara, H&M, …) (USD)',
 '1 Pair of Nike Running Shoes (Mid-Range) (USD)',
 '1 Pair of Men Leather Business Shoes (USD)',
 'Apartment (1 bedroom) in City Centre (USD)',
 'Apartment (1 bedroom) Outside of Centre (USD)',
 'Apartment (3 bedrooms) in City Centre (USD)',
 'Apartment (3 bedrooms) Outside of Centre (USD)',
 'Price per Square Meter to Buy Apartment in City Centre (USD)',
 'Price per Square Meter to Buy Apartment Outside of Centre (USD)',
 'Average Monthly Net Salary (After Tax) (USD)',
 'Mortgage Interest Rate in Percentages (%), Yearly, for 20 Years Fixed-Rate',
 '0 if Numbeo considers that more contributors are needed to increase data quality, else 1']
index = ['index']
