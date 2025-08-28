import React, { useState, useEffect, useRef, forwardRef } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  FlatList,
  Image,
  ActivityIndicator,
  StyleSheet
} from 'react-native';
import { useDispatch, useSelector } from 'react-redux';
import {
  setIsValidSelection,
  setSelectedAirportsList
} from '@picotrip/shared/src/store/actions/tripOrganisationActions';
import { sendCoordinates } from '@picotrip/shared/src/utils/geolocation';

// icons/images (adjust paths for RN asset system)
import LocationImage from "@picotrip/shared/assets/images/my-location-svgrepo-com.svg";
import CheckMark from "@picotrip/shared/assets/images/check-mark-svgrepo-com.svg";

import { styles } from './styles'; // optional if separate file

const Autocomplete = forwardRef(({
  startingPoint,
  setStartingPoint,
  onNextClick,
  onOriginChange,
  airportList,
  xButtonDisplayed
}, ref) => {
  const [results, setResults] = useState([]);
  const [dropdownVisible, setDropdownVisible] = useState(false);
  const [isFetchingLocation, setIsFetchingLocation] = useState(false);
  const [inputValue, setInputValue] = useState(startingPoint || "");

  const dispatch = useDispatch();
  const selectedAirports = useSelector(state => state.tripOrganisation.selectedAirportsList);
  const isValidSelection = useSelector(state => state.tripOrganisation.isValidSelection);

  useEffect(() => {
    if (inputValue.length >= 2 && dropdownVisible) {
      let path;
      if (process.env.VITE_WORKMODE === 'dev') {
        path = `http://${process.env.VITE_URL}:${process.env.VITE_DJANGO_PORT}/api/autocomplete_airports/?input=${inputValue}`;
      } else {
        path = `/api/autocomplete_airports/?input=${inputValue}`;
      }

      fetch(path)
        .then(res => res.json())
        .then(data => {
          const formattedResults = data.message.map(item => ({
            city: item.city,
            country: item.country,
            admin_name: item.admin_name,
            id: item.id
          }));
          setResults(formattedResults.slice(0, 10));
          setDropdownVisible(true);
        })
        .catch(err => console.error(err));
    } else {
      setResults([]);
      setDropdownVisible(false);
    }
  }, [inputValue, dropdownVisible]);

  useEffect(() => {
    setInputValue(startingPoint || '');
  }, [startingPoint]);

  const clearInput = () => {
    setInputValue('');
    setStartingPoint?.('');
    setResults([]);
    setDropdownVisible(false);
    dispatch(setIsValidSelection(false));
  };

  const handleGetLocation = () => {
    setIsFetchingLocation(true);
    sendCoordinates(
      ({ location, originId }) => {
        setInputValue(location);
        dispatch(setIsValidSelection(true));
        setStartingPoint?.(location);
        onOriginChange?.(originId);
      },
      (err) => console.error("Location error", err)
    ).finally(() => setIsFetchingLocation(false));
  };

  const onItemClick = (item) => {
    const text = `${item.city}, ${item.country}, ${item.admin_name}`;
    setInputValue(text);
    setStartingPoint?.(text);
    dispatch(setIsValidSelection(true));
    onOriginChange?.(item.id);
    setResults([]);
    setDropdownVisible(false);
  };

  return (
    <View style={styles.container}>
      <TextInput
        value={inputValue}
        onChangeText={text => {
          setInputValue(text);
          setStartingPoint?.(text);
          dispatch(setIsValidSelection(false));
          setDropdownVisible(true);
        }}
        placeholder="Starting Point"
        style={styles.input}
        ref={ref}
      />

      {isFetchingLocation ? (
        <ActivityIndicator />
      ) : (
        <TouchableOpacity onPress={handleGetLocation}>
          <Image source={LocationImage} style={styles.icon} />
        </TouchableOpacity>
      )}

      {dropdownVisible && results.length > 0 && (
        <FlatList
          data={results}
          keyExtractor={(item) => item.id.toString()}
          renderItem={({ item }) => (
            <TouchableOpacity onPress={() => onItemClick(item)} style={styles.resultItem}>
              <Text>{item.city}, {item.country}, {item.admin_name}</Text>
            </TouchableOpacity>
          )}
        />
      )}

      {isValidSelection && airportList.length > 0 && (
        <View style={styles.airportsContainer}>
          {airportList.map(airport => {
            const isSelected = selectedAirports.includes(airport.iata_code);
            return (
              <TouchableOpacity
                key={airport.iata_code}
                style={[styles.airportButton, isSelected && styles.selected]}
                onPress={() => {
                  const updatedList = isSelected
                    ? selectedAirports.filter(code => code !== airport.iata_code)
                    : [...selectedAirports, airport.iata_code];
                  dispatch(setSelectedAirportsList(updatedList));
                }}
              >
                <Text>{airport.iata_code} - {airport.name}, {airport.iso_country}</Text>
                {isSelected && <Image source={CheckMark} style={styles.checkIcon} />}
              </TouchableOpacity>
            );
          })}
        </View>
      )}

      <TouchableOpacity onPress={onNextClick} style={styles.nextButton}>
        <Text style={styles.nextButtonText}>Next</Text>
      </TouchableOpacity>
    </View>
  );
});

export default Autocomplete;