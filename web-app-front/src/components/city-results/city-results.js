import classNames from 'classnames';
import styles from './city-results.module.scss';
import { useGetResultsQuery } from 'services/api';
import { useState, useEffect } from 'react';

function CityResult({ result }) {
    const { crashes, city, startDate, endDate } = result;
    return (
        <li className={styles.result}>
            <p className={styles.city}>{city}</p>
            <p className={styles.date}>
                {startDate}
                {' — '}
                {endDate}
            </p>
            <p className={styles.crashes}>{crashes}</p>
        </li>
    );
}

const searchFields = ['city', 'crashes', 'startDate', 'endDate'];

function CityResults({ className }) {
    const { data, isLoading, isSuccess } = useGetResultsQuery();

    const [search, setSearch] = useState('');
    const handleInputChange = event => setSearch(event.target.value);

    const [filteredData, setFilteredData] = useState([]);
    useEffect(() => {
        if (isSuccess) {
            setFilteredData(
                data?.filter(result =>
                    searchFields.some(field =>
                        result[field]
                            .toString()
                            .toLowerCase()
                            .includes(search.toLocaleLowerCase().trim()),
                    ),
                ),
            );
        }
    }, [search, data, isSuccess]);

    return (
        <div className={className}>
            <input
                className={styles.search}
                value={search}
                placeholder="Найти"
                onChange={handleInputChange}
            />
            {isLoading && <p>Loading...</p>}
            {isSuccess && (
                <ul className={styles.results}>
                    {filteredData?.map(result => (
                        <CityResult key={result.id} result={result} />
                    ))}
                </ul>
            )}
        </div>
    );
}

export default CityResults;
