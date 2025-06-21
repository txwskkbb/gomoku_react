import React from 'react';
import './Board.css'; // 我们将为棋盘创建单独的CSS

const EMPTY = 0;
const PLAYER = 1;
const AI = 2;

const Board = ({ board, onCellClick, disabled }) => {
  return (
    <div className="board">
      {board.map((row, rowIndex) => (
        <div key={rowIndex} className="board-row">
          {row.map((cell, colIndex) => (
            <div
              key={colIndex}
              className={`cell ${disabled ? 'disabled' : ''}`}
              onClick={() => !disabled && onCellClick(rowIndex, colIndex)}
            >
              {cell === PLAYER && <div className="stone player"></div>}
              {cell === AI && <div className="stone ai"></div>}
            </div>
          ))}
        </div>
      ))}
    </div>
  );
};

export default Board;
