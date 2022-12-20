const { Prediction } = require('../models');
const { asyncMiddleware } = require('../middlewares/async.middleware');
const { AppError } = require('../middlewares/error.middleware');

async function getPredictions(req, res) {
    const today = new Date();
    const yesterday = new Date();
    yesterday.setDate(yesterday.getDate() - 10);

    const data = await Prediction.find({
        endDate: {
            $gte: yesterday,
            $lt: today,
        },
    });

    if (!data) {
        throw new AppError('Not found.', 401);
    }

    res.json({
        predictions: data,
        today: today,
        yesterday: yesterday,
    });
}

module.exports = {
    getPredictions: asyncMiddleware(getPredictions),
};
