import { Provider } from 'react-redux';
import store from 'store';
import MainLayout from 'components/layouts/main-layout';
import CityResults from 'components/city-results';

function App() {
    return (
        <Provider store={store}>
            <MainLayout>
                <CityResults className="col-10 m-4" />
            </MainLayout>
        </Provider>
    );
}

export default App;
