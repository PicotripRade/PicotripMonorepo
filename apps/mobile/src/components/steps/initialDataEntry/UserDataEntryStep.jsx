import React, {useState, useEffect, useRef} from "react";
import {View, Text, TouchableOpacity, StyleSheet, ActivityIndicator} from "react-native";
import {useDispatch, useSelector} from "react-redux";
import AsyncStorage from "@react-native-async-storage/async-storage";
import {useNavigation, useRoute} from "@react-navigation/native";
import { styles } from './styles';

import {addCityInfo} from "@picotrip/shared/src/store/actions/cityInformationActions";
import {
    setArrowBackPressed,
    setCalendarOpen,
    setIsValidSelection,
    setSelectedAirportsList,
    setTagsExpanded,
    setWhereFromExpanded,
} from "@picotrip/shared/src/store/actions/tripOrganisationActions";

import {
    fetchAirports,
    fetchUserLocation,
    formatDateToNumbersAndLetters,
    formatDisplayDate,
    handleCitySelect,
    getTagDescription,
} from "@picotrip/shared";

import {
    setSearchResultsDisplayed,
    setSearchResultsReady,
} from "@picotrip/shared/src/store/actions/searchResultsActions";
import {handleSearchClick} from "@picotrip/shared/src/utils/handleSearchClick";

// Replace web components with React Native versions
import Autocomplete from "../../autocomplete/AutocompleteRN";
import CustomCalendar from "../../datepicker/CustomCalendarRN";
import TagSelection from "../../tagSelection/TagSelectionRN";
import SearchResults from "../../searchResults/SearchResultsRN";
import CustomButton from "../../buttons/CustomButtonRN";


export default function UserDataEntryStep() {
    const dispatch = useDispatch();
    const navigation = useNavigation();
    const route = useRoute();

    const [inputFieldsCollapsed, setInputFieldsCollapsed] = useState(false);
    const [startingPoint, setStartingPoint] = useState("");
    const [originId, setOriginId] = useState("");
    const [selectedTag, setSelectedTag] = useState("");
    const [isLoading, setIsLoading] = useState(false);

    const startDate = useSelector((state) => state.tripOrganisation.startDate);
    const endDate = useSelector((state) => state.tripOrganisation.endDate);
    const isValidSelection = useSelector((state) => state.tripOrganisation.isValidSelection);
    const airportsListRedux = useSelector((state) => state.tripOrganisation.airportList);


    useEffect(() => {
        const fetchLocation = async () => {
            const {city, country, id} = await fetchUserLocation();
            const response_formatted = `${city}, ${country}`;

            await AsyncStorage.setItem("geoname", id);
            setOriginId(id);
            setStartingPoint(response_formatted);
            dispatch(setIsValidSelection(true));

            fetchAirports({id, dispatch});
        };
        fetchLocation();
    }, []);

    const onSearchClick = () => {
        handleSearchClick({
            overrideParams: null,
            skipUpdateURL: false,
            startDate,
            endDate,
            originId,
            selectedTag,
            airportsList: airportsListRedux,
            startingPoint,
            dispatch,
            navigate: navigation.navigate,
            setSearchResultsDisplayed,
            setSearchResultsReady,
            setIsLoading,
        });
    };

    return (
        <View style={styles.container}>
            {isLoading ? (
                <ActivityIndicator size="large"/>
            ) : (
                <>
                    <Autocomplete
                        startingPoint={startingPoint}
                        onOriginChange={setOriginId}
                        airportList={airportsListRedux}
                    />

                    <CustomCalendar
                        startDate={startDate}
                        endDate={endDate}
                        onClose={() => dispatch(setCalendarOpen(false))}
                    />

                    <TagSelection selectedTag={selectedTag} onTagChange={setSelectedTag}/>

                    <CustomButton label="Search" onPress={onSearchClick}/>

                    <SearchResults loading={isLoading}/>
                </>
            )}
        </View>
    );
}

const styles = StyleSheet.create({
    container: {flex: 1, padding: 16, backgroundColor: "#fff"},
});
