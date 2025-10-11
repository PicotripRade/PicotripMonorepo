import { StyleSheet } from 'react-native';

export const styles = StyleSheet.create({
  autocomplete: {
    marginHorizontal: 'auto',
    position: 'relative',
    width: '100%',
    backgroundColor: '#E0E0E0', // replace with var(--element-background)
  },
  autocompleteResults: {
    listStyleType: 'none',
    position: 'relative',
    left: '50%',
    transform: [{ translateX: -0.5 * 100 + '%' }], // approximate
    width: '95%',
    zIndex: 1,
    margin: 0,
    padding: 0,
    height: 340,
    overflow: 'hidden',
  },
  autocompleteItem: {
    cursor: 'pointer', // not functional in RN
    fontSize: 15,
    borderBottomWidth: 1,
    borderBottomColor: '#333333', // replace with var(--background-dark)
    paddingVertical: 8,
  },
  last: {
    borderBottomWidth: 0,
  },
  first: {
    borderTopWidth: 0,
  },
  name: {
    color: '#000000', // var(--text-color)
  },
  code: {
    color: '#000000',
    fontWeight: 'bold',
    marginLeft: 10,
  },
  edgeBlock: {
    width: '100%',
    marginHorizontal: 'auto',
    borderRadius: 5,
    boxSizing: 'border-box', // ignored in RN
    position: 'relative',
    overflow: 'hidden',
    backgroundColor: '#E0E0E0', // var(--element-background)
    display: 'flex',
    flexDirection: 'row',
    transition: 'height 0.3s', // ignored in RN
  },
  innerBlock: {
    position: 'relative',
    width: '100%',
    backgroundPosition: '0 0', // ignored
    backgroundSize: 'auto', // ignored
  },
  innerBlockExpanded: {
    display: 'flex',
    flexDirection: 'column',
    height: '85%',
  },
  innerBlockExpandedDecreasedHeight: {
    height: '80%',
  },
  locationBlock: {
    position: 'relative',
    width: 40,
    marginHorizontal: 'auto',
    backgroundColor: '#888888', // var(--monitor-shadow-color)
    height: 42,
    borderLeftWidth: 1,
    borderLeftColor: '#CCCCCC', // var(--border-color)
  },
  locationBlockImage: {
    width: '70%',
    height: '100%',
  },
  destinationInputField: {
    position: 'relative',
    width: '90%',
    borderWidth: 1,
    borderColor: '#CCCCCC', // var(--border-color)
    marginTop: 10,
    marginHorizontal: 'auto',
    display: 'flex',
    flexDirection: 'row',
  },
  inputContainer: {
    position: 'relative',
  },
  placeholderText: {
    position: 'absolute',
    top: '50%',
    width: '95%',
    transform: [{ translateY: -0.5 * 100 + '%' }], // approximate centering
    color: '#AAAAAA', // var(--disabled-text)
    pointerEvents: 'none',
    zIndex: 30,
  },
  input: {
    width: '90%',
    padding: 10,
    textAlign: 'center',
    borderWidth: 0,
    backgroundColor: '#DDDDDD', // var(--background-less-dark)
    color: '#000000', // var(--text-color)
    fontSize: 16,
    fontFamily: 'Aspira',
  },
  inputCollapsed: {
    textAlign: 'right',
    backgroundColor: '#E0E0E0', // var(--element-background)
  },
  disabledText: {
    color: '#888888', // var(--accent-text)
    fontSize: 18,
    marginHorizontal: 'auto',
    paddingLeft: 10,
    fontFamily: 'Aspira',
  },
  inputNavigation: {
    width: '100%',
    height: 90,
    alignItems: 'center',
    display: 'flex',
    flexDirection: 'row',
  },
  emptySpace: {
    flexGrow: 1,
  },
  airportCheckboxList: {
    display: 'flex',
    flexDirection: 'column',
    gap: 10,
  },
  label: {
    display: 'flex',
    marginBottom: 5,
    flexDirection: 'row',
    width: 80,
  },
  checkboxInput: {
    backgroundColor: '#888888', // var(--monitor-shadow-color)
    width: 20,
  },
  sectionTitle: {
    fontStyle: 'italic',
    fontSize: 12,
    fontFamily: 'Aspira',
    color: '#000000', // var(--text-color)
    textAlign: 'left',
    paddingLeft: 16,
    marginVertical: 23,
  },
  airportTextWrapper: {
    display: 'flex',
    flexDirection: 'column',
    width: 'calc(100% + 24px)', // may need adjustment
  },
  checkboxHidden: {
    width: 24,
    opacity: 0,
  },
});
