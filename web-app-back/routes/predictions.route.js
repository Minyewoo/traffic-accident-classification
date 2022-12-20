const express = require('express');
const { getPredictions } = require('../controllers/prediction.controller');

const predictionsRouter = express.Router();
predictionsRouter.get('/', getPredictions);

module.exports = predictionsRouter;
