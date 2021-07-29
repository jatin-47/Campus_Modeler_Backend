const bcrypt = require('bcrypt');

module.exports = (sequelize, DataTypes) => {
    const User = sequelize.define('User', {
        username: {
            type: DataTypes.STRING,
            allowNull: false,
            validate: {
                notEmpty: true
            },
            unique: true,
        },
        password: {
            type: DataTypes.STRING,
            allowNull: false,
            validate: {
                notEmpty: true
            },
        },
    },
        {
            tableName: 'users'
        });

    User.prototype.toString = function () {
        return this.username;
    }

    User.prototype.verifyPassword = async function (password) {
        return await bcrypt.compare(password, this.password);
    }

    User.afterValidate(async (user, options) => {
        if (user.changed('password')) {
            const salt = await bcrypt.genSalt(10);
            user.password = await await bcrypt.hash(user.password, salt);
        }
    });
    return User;
};