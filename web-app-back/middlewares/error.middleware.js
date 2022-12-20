class AppError extends Error {
    constructor(message, statusCode) {
        super(message);
        this.statusCode = statusCode;
    }
}

const handleAppError = (err, req, res) => {
    const { message, statusCode = 500 } = err;

    res.status(statusCode).json({
        error: {
            status: statusCode,
            message,
        },
    });
};

const handleUnknownError = (err, req, res) => {
    res.status(500).json({
        error: {
            status: 500,
            message: 'Internal server error',
            debugMessage: err.message,
        },
    });
};

const errorHandler = (err, req, res, next) => {
    if (err instanceof AppError) {
        handleAppError(err, req, res);
    } else {
        handleUnknownError(err, req, res);
    }
};

const notFoundPathHandler = (req, res, next) =>
    next(new AppError('Not found', 404));

module.exports = {
    AppError,
    errorHandler,
    notFoundPathHandler,
};
