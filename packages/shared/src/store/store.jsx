import { createStore } from 'redux';
import rootReducer from "./reducers/rootReducer.jsx";

const store = createStore(
  rootReducer,
  // Optionally include Redux DevTools extension support
  window.__REDUX_DEVTOOLS_EXTENSION__ && window.__REDUX_DEVTOOLS_EXTENSION__()
);

export default store;
