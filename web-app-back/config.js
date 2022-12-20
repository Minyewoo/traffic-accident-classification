module.exports = {
    APP_PORT: 8080,
    DB_PORT: 27017,
    DB_HOST: process.env.MONGO_HOST,
    DB_USERNAME: process.env.MONGO_USERNAME,
    DB_PASSWORD: process.env.MONGO_PASSWORD,
    DB_NAME: process.env.DB_NAME,
    DB_COLLECTION: process.env.DB_COLLECTION,
};
