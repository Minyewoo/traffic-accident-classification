const cors = require('cors');

const corsOptions = {
    origin: '*',
};

exports.corsMiddleware = cors(corsOptions);
