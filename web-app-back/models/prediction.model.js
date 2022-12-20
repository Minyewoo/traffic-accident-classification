const mongoose = require('mongoose');
const { Schema } = mongoose;
const { DB_COLLECTION } = require('../config');

const PredictionSchema = new Schema(
    {
        city: {
            type: String,
            required: true,
        },
        crashes: {
            type: Number,
            required: true,
        },
        startDate: {
            type: Date,
            required: true,
        },
        endDate: {
            type: Date,
            required: true,
        },
    },
    {
        collection: DB_COLLECTION,
    },
);

module.exports = mongoose.model('Prediction', PredictionSchema);
