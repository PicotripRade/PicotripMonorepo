import { StyleSheet, Dimensions } from 'react-native';

const { width: screenWidth } = Dimensions.get('window');

export const styles = StyleSheet.create({
  autocompleteWrapper: {
    width: screenWidth > 330 ? 300 : 250, // replace with var(--container-width-smartphone/tiny-smartphone)
    marginHorizontal: 'auto',
  },
  svgIconNavDisabled: {
    opacity: 0.5,
    // cursor: 'not-allowed', // not supported in RN
  },
  inputField: {
    display: 'flex',
    width: '80%',
    minHeight: 28,
    padding: 5,
    position: 'relative',
    justifyContent: 'center',
    alignItems: 'center',
    marginHorizontal: 'auto',
    fontSize: 18,
    boxSizing: 'border-box', // RN doesn’t need box-sizing
  },
  timeRangeBox: {
    display: 'flex',
    flexDirection: 'row',
    backgroundColor: '#f0f0f0', // placeholder for --element-background
  },
  dateRangeInfoWrapper: {
    width: '100%',
    display: 'flex',
    flexDirection: 'row',
    justifyContent: 'flex-end',
    alignItems: 'flex-end',
  },
  dateRangeInfo: {
    height: 35,
    width: 180,
    display: 'flex',
    justifyContent: 'flex-end',
    alignItems: 'flex-end',
    marginRight: 10,
  },
  rangeDisplay: {
    height: 25,
    borderRadius: 5,
    marginVertical: 0,
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    fontSize: 13,
    fontWeight: 'bold',
    fontFamily: 'Aspira',
    color: '#333', // placeholder for --text-color
  },
  rangeDisplayUnselected: {
    color: '#aaa', // placeholder for --disabled-text
  },
  navigation: {
    display: 'flex',
    flexDirection: 'row',
    marginHorizontal: 'auto',
  },
  datepickerWrapper: {
    display: 'flex',
    flexDirection: 'row',
  },
  timeRangeContainer: {
    marginHorizontal: 'auto',
    width: screenWidth > 350 ? 300 : 250, // responsive width
    backgroundColor: '#f0f0f0', // placeholder for --element-background
  },
  counterWrapper: {
    marginHorizontal: 'auto',
    width: screenWidth > 350 ? 300 : 250,
    backgroundColor: '#f0f0f0',
  },
  itemLabel: {
    display: 'flex',
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    height: 14,
    marginBottom: 2,
  },
  labelTime: {
    color: '#888', // placeholder for --border-color
    fontSize: 11,
    opacity: 0.7,
  },
  labelDescription: {
    color: '#888',
    fontSize: 11,
    opacity: 0.7,
  },
  initialDataLabel: {
    color: '#888',
    fontSize: 12,
    display: 'flex',
    justifyContent: 'flex-start',
    height: 6,
  },
  shortDataLabel: {
    color: '#333', // placeholder for --background-dark
    fontSize: 12,
    display: 'flex',
    justifyContent: 'flex-start',
    height: 6,
    width: 50,
  },
  travelTypeSelection: {
    display: 'flex',
    flexDirection: 'row',
    width: screenWidth > 350 ? 300 : 250,
    marginVertical: 5,
    marginHorizontal: 'auto',
    marginBottom: -8,
  },
  allTypes: {
    width: '33%',
    marginTop: 15,
  },
  byCar: {
    width: '33%',
    marginTop: 15,
  },
  byPlane: {
    width: '33%',
    marginTop: 15,
  },
  typeLabel: {
    fontSize: 15,
    fontFamily: 'Arial',
    fontWeight: 'bold',
    marginBottom: 2,
  },
  typeSelected: {
    borderBottomWidth: 2,
    borderBottomColor: '#ccc', // placeholder for --monitor-shadow-color
  },
  resultsContainer: {
    height: '100%',
  },
  userEntryContainer: {
    display: 'flex',
    flexDirection: 'column',
    gap: 15,
    paddingTop: 20,
  },
  collapsedInputWrapper: {
    display: 'flex',
    flexDirection: 'row',
    width: 320,
    marginHorizontal: 'auto',
    alignItems: 'center',
  },
  collapsedInput: {
    height: 60,
    width: 220,
    fontFamily: 'Arial',
    display: 'flex',
    alignItems: 'center',
    borderRadius: 45,
    backgroundColor: '#f0f0f0',
    marginHorizontal: 'auto',
    flexDirection: 'column',
    justifyContent: 'center',
  },
  activityNameCollapsed: {
    fontSize: 16,
    fontWeight: 'bold',
    fontFamily: 'Aspira',
    color: '#333', // placeholder for --text-color
    marginBottom: 8,
  },
  timeRangeCollapsed: {
    fontSize: 14,
    fontFamily: 'Arial',
    color: 'black',
  },
  xButtonResults: {
    width: screenWidth > 330 ? 300 : 250,
    marginHorizontal: 'auto',
    display: 'flex',
    alignItems: 'flex-start',
    paddingLeft: 12,
  },
  filterResultsImg: {
    width: 35,
    height: 35,
  },
  backArrowResultsImg: {
    width: 35,
    height: 35,
  },
  searchAgainButton: {
    color: '#f00', // placeholder for --accent-text
    padding: 5,
    fontSize: 14,
  },
});
