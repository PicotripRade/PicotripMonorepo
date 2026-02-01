import React, {useState, useEffect} from "react";
import {
    View,
    Text,
    Image,
    TouchableOpacity,
    ScrollView,
    Modal,
    StyleSheet,
    ActivityIndicator,
} from "react-native";
import {useDispatch} from "react-redux";
import {setSelectedCityRedux} from "@picotrip/shared/src/store/actions/cityInformationActions";
import {formatDateToMonthDayYear, getCountryName, removeTextInBrackets} from "@picotrip/shared";

// TODO: replace with RN-friendly components
import RadarScan from "../sonarAnimation/SonarRN";
import FlightSegment from "./FlightSegmentRN";

const SearchResults = ({
                           loading,
                           ready,
                           data,
                           typeToDisplay,
                           onCitySelect,
                           cityInfo,
                           isLoadingCityData,
                           startDate,
                           finalDate,
                       }) => {
    const SENTENCE_TIME_MILLISECONDS = 3000;
    const DOTS_TIME_MILLISECONDS = 500;

    const dispatch = useDispatch();

    const loadingSentences = [
        "Analyzing 5000+ destinations",
        "Finding flights",
        "Calculating routes",
        "Optimizing offers",
    ];

    const [loadingIndex, setLoadingIndex] = useState(0);
    const [dotCount, setDotCount] = useState(0);
    const [selectedCity, setSelectedCity] = useState(null);

    useEffect(() => {
        if (loading) {
            const sentenceInterval = setInterval(() => {
                setLoadingIndex((prevIndex) => (prevIndex + 1) % loadingSentences.length);
            }, SENTENCE_TIME_MILLISECONDS);
            return () => clearInterval(sentenceInterval);
        } else {
            setLoadingIndex(0);
        }
    }, [loading]);

    useEffect(() => {
        if (loading) {
            const dotInterval = setInterval(() => {
                setDotCount((prevCount) => (prevCount + 1) % 4);
            }, DOTS_TIME_MILLISECONDS);
            return () => clearInterval(dotInterval);
        } else {
            setDotCount(0);
        }
    }, [loading]);

    const typeMap = {
        1: "top",
        2: "flight",
        3: "car",
    };

    let filteredData = [];

    if (data && data.results) {
        const selectedType = typeMap[typeToDisplay] || "top";
        const rawData = data.results[selectedType];
        if (selectedType === "flight") {
            filteredData = rawData.filter((city) => city.transport === "direct");
        } else {
            console.log("no direct flights");
        }
        filteredData = Array.isArray(rawData) ? rawData : [];
    }

    const handleTeaserClick = (city) => {
        setSelectedCity(city);
        dispatch(setSelectedCityRedux(city.geonameid));
        onCitySelect({
            geonameid: city.geonameid,
            transportType: city.transport,
            cityName: city.name,
            countryName: getCountryName(city.country_code),
        });
    };

    const closeModal = () => {
        setSelectedCity(null);
    };

    if (loading) {
        return (
            <View style={styles.resultsWrapper}>
                <RadarScan useIcons={false} />
                <Text style={styles.loadingText}>
                    {loadingSentences[loadingIndex]}
                    {".".repeat(dotCount)}
                </Text>
            </View>
        );
    }

    if (ready) {
        return (
            <View style={styles.resultsWrapper}>
                <ScrollView contentContainerStyle={styles.scrollWrapper}>
                    {filteredData.length > 0 ? (
                        filteredData.map((city) => (
                            <TouchableOpacity
                                key={city.geonameid}
                                style={styles.cityTeaser}
                                onPress={() => handleTeaserClick(city)}
                            >
                                <Image source={{uri: city.image || "https://placehold.co/300x200"}}
                                       style={styles.cityImage}/>
                                <View style={styles.description}>
                                    <View style={styles.mainDesc}>
                                        <View style={styles.leftInfo}>
                                            <Text style={styles.cityName}>{city.name}</Text>
                                            <Text style={styles.countryName}>{getCountryName(city.country_code)}</Text>
                                        </View>
                                        <View style={{flex: 1}}/>
                                        <View style={styles.rightInfo}>
                                            {city.transport === "direct" && (
                                                <View>
                                                    <Text>
                                                        from <Text
                                                        style={styles.departure}>{city.departures[0].departure}</Text>
                                                    </Text>
                                                    <Text>
                                                        via <Text
                                                        style={styles.departure}>{removeTextInBrackets(city.departures[0]["airline:"])}</Text>
                                                    </Text>
                                                </View>
                                            )}
                                            <Text style={styles.transportLabel}>
                                                {city.transport === "direct" ? "Direct" : city.transport}
                                            </Text>
                                        </View>
                                    </View>
                                    <View style={styles.footerDesc}>
                                        {city.PK_no_h5_1 > 0 && <Text>{`PEAKS ${city.PK_no_h5_1}`}</Text>}
                                        {city.MT_no_h5_1 > 0 && <Text>{`MOUNTAINS ${city.MT_no_h5_1}`}</Text>}
                                        {city.BCH_no_h6_1 > 0 && <Text>{`BCH ${city.BCH_no_h6_1}`}</Text>}
                                    </View>
                                </View>
                            </TouchableOpacity>
                        ))
                    ) : (
                        <Text>No results found.</Text>
                    )}
                </ScrollView>

                {/* Modal popup */}
                <Modal visible={!!selectedCity} animationType="slide" transparent>
                    <View style={styles.modalOverlay}>
                        <View style={styles.modalContent}>
                            <TouchableOpacity style={styles.closeButton} onPress={closeModal}>
                                <Text style={styles.closeText}>×</Text>
                            </TouchableOpacity>
                            {selectedCity && (
                                <>
                                    <Text style={styles.modalTitle}>{selectedCity.name}</Text>
                                    <Text style={styles.modalCountry}>{getCountryName(selectedCity.country_code)}</Text>

                                    {/* 🔽 ADD FLIGHT SEGMENTS HERE */}
                                    {selectedCity.departures && selectedCity.departures.length > 0 && (
                                        <View style={{marginTop: 12}}>
                                            <Text style={styles.sectionTitle}>Flight Segments</Text>
                                            {selectedCity.departures.map((segment, idx) => (
                                                <FlightSegment key={idx} segment={segment}/>
                                            ))}
                                        </View>
                                    )}
                                    {/* 🔼 END FLIGHT SEGMENTS */}

                                    {isLoadingCityData ? (
                                        <ActivityIndicator size="large"/>
                                    ) : (
                                        <ScrollView style={{marginTop: 12}}>
                                            {cityInfo?.what_attraction_to_visit_regarding_activity && (
                                                <>
                                                    <Text style={styles.sectionTitle}>Must See</Text>
                                                    {cityInfo.what_attraction_to_visit_regarding_activity.map((attr, idx) => (
                                                        <Text key={idx}>• {attr}</Text>
                                                    ))}
                                                </>
                                            )}
                                            {cityInfo?.what_is_best_to_do_on_chosen_dates && (
                                                <>
                                                    <Text style={styles.sectionTitle}>Recommendations</Text>
                                                    {Object.entries(cityInfo.what_is_best_to_do_on_chosen_dates).map(([date, activity]) => (
                                                        <View key={date}>
                                                            <Text
                                                                style={styles.dateFont}>{formatDateToMonthDayYear(date)}</Text>
                                                            <Text>{activity}</Text>
                                                        </View>
                                                    ))}
                                                </>
                                            )}
                                        </ScrollView>
                                    )}
                                </>
                            )}
                        </View>
                    </View>
                </Modal>
            </View>
        );
    }

    return null;
};

const styles = StyleSheet.create({
    resultsWrapper: {flex: 1, alignItems: "center", justifyContent: "center"},
    loadingText: {marginTop: 16, fontSize: 16},
    scrollWrapper: {padding: 12},
    cityTeaser: {
        backgroundColor: "#fff",
        marginBottom: 12,
        borderRadius: 12,
        overflow: "hidden",
        elevation: 3,
    },
    cityImage: {width: "100%", height: 150},
    description: {padding: 12},
    mainDesc: {flexDirection: "row", alignItems: "center"},
    leftInfo: {flexDirection: "column"},
    cityName: {fontSize: 18, fontWeight: "bold"},
    countryName: {fontSize: 14, color: "#666"},
    rightInfo: {flexDirection: "column", alignItems: "flex-end"},
    departure: {fontWeight: "bold"},
    transportLabel: {marginTop: 4, fontSize: 12, color: "#007AFF"},
    footerDesc: {marginTop: 8, flexDirection: "row", flexWrap: "wrap", gap: 6},
    modalOverlay: {
        flex: 1,
        backgroundColor: "rgba(0,0,0,0.6)",
        justifyContent: "center",
        alignItems: "center",
    },
    modalContent: {
        backgroundColor: "#fff",
        borderRadius: 12,
        padding: 16,
        width: "90%",
        maxHeight: "80%",
    },
    closeButton: {alignSelf: "flex-end"},
    closeText: {fontSize: 22, fontWeight: "bold"},
    modalTitle: {fontSize: 20, fontWeight: "bold", marginBottom: 4},
    modalCountry: {fontSize: 16, color: "#666"},
    sectionTitle: {marginTop: 12, fontWeight: "bold"},
    dateFont: {marginTop: 8, fontWeight: "600"},
});

export default SearchResults;
