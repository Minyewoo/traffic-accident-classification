import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';
import dayjs from 'dayjs';
import 'dayjs/locale/ru';

dayjs.locale('ru');

const formatDate = date => dayjs(date).format('DD.MM.YYYY HH:mm:ss');

const getCrashWord = number => {
    const units = number % 10;
    const value = number % 100;
    if (value > 1 && value < 5) return 'аварии';
    if (units > 10 && units < 20) return 'аварий';
    if (units === 1) return 'авария';
    return 'аварий';
};

const cityNames = {
    msc: 'Москва',
    spb: 'Санкт-Петербург',
};
const getCityName = city => cityNames[city] ?? city;

const transformResultsData = ({ predictions }) =>
    predictions.map(result => ({
        id: result._id,
        crashes: `${result.crashes} ${getCrashWord(result.crashes)}`,
        city: getCityName(result.city),
        startDate: formatDate(result.startDate),
        endDate: formatDate(result.endDate),
    }));

export const api = createApi({
    reducerPath: 'api',
    baseQuery: fetchBaseQuery({ baseUrl: `http://${process.env.REACT_APP_API_URL}` }),
    endpoints: builder => ({
        getResults: builder.query({
            query: () => 'predictions',
            transformResponse: response => transformResultsData(response),
        }),
    }),
});

export const { useGetResultsQuery } = api;
