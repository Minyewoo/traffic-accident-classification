const mongoose = require('mongoose');
const Prediction = require('./prediction.model');
const {
    DB_HOST,
    DB_PORT,
    DB_USERNAME,
    DB_PASSWORD,
    DB_NAME,
} = require('../config');

const uri = `mongodb://${DB_USERNAME}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}?authSource=admin`;
const options = {
    useNewUrlParser: true,
    useUnifiedTopology: true,
};

const init = async () => {
    try {
        await mongoose.connect(uri, options);
    } catch (err) {
        throw Error(`Failed to connect to ${uri} MongoDB database.\n${err}`);
    }
};

module.exports = {
    init,
    Prediction,
};
