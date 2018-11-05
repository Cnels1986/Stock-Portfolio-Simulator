CREATE DATABASE stocksdb;
USE stocksdb;
DROP TABLE IF EXISTS `Users`;
DROP TABLE IF EXISTS `Wallet`;
DROP TABLE IF EXISTS `Stocks`;
DROP TABLE IF EXISTS `Portfolio`;

-- creates the table that will store the user's username and hashed password
CREATE TABLE `Users` (
  `id` int(11) NOT NULL AUTO_INCREMENT UNIQUE,
  `username` varchar(40) NOT NULL UNIQUE,
  `password` varchar(100) NOT NULL,
  `name` varchar(40) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- creates the table that will store the users money left in their wallet, will be updated whenever the user buys or sells stocks from the app at their current price
CREATE TABLE `Wallet` (
  `id` int(11) NOT NULL AUTO_INCREMENT UNIQUE,
  `user_id` int(11) NOT NULL UNIQUE,
  `money` decimal(11) NOT NULL,
  PRIMARY KEY(`id`),
  FOREIGN KEY(`user_id`) REFERENCES Users(`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- creates the table that will store the name and symbol of the stocks that have been looked up, will be used with the portfolio table
CREATE TABLE `Stocks` (
  `id` int(11) NOT NULL AUTO_INCREMENT UNIQUE,
  `symbol` varchar(20) NOT NULL UNIQUE,
  `name` varchar(100) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- creates the table that will store the user's portfolio which will contain the stocks the user buys, the amount they bought and the price they bought it at
CREATE TABLE `Portfolio` (
  `id` int(11) NOT NULL AUTO_INCREMENT UNIQUE,
  `user_id` int(11) NOT NULL,
  `stock_id` int(11) NOT NULL,
  `amount` int(11) NOT NULL,
  `price` decimal(11) NOT NULL,
  PRIMARY KEY(`id`),
  FOREIGN KEY(`user_id`) REFERENCES Users(`id`),
  FOREIGN KEY(`stock_id`) REFERENCES Stocks(`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
