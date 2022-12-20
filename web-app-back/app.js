const express = require('express');
const db = require('./models');
const predictions = require('./routes/predictions.route');
const { corsMiddleware } = require('./middlewares/cors.middleware');
const {
    errorHandler,
    notFoundPathHandler,
} = require('./middlewares/error.middleware');

const app = express();

// middlewares
app.use(corsMiddleware);
app.use(express.json());
// routes
app.use('/predictions', predictions);
// error handlers
app.use(notFoundPathHandler);
app.use(errorHandler);

exports.app = {
    start: async () => {
        try {
            await db.init();
            app.listen(8080, () => {
                console.log('App started');
            });
        } catch (err) {
            console.error(err);
        }
    },
};
