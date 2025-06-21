import React, { useState, useEffect, useCallback } from 'react';
import Board from './components/Board';
import './App.css';

const API_URL = 'http://127.0.0.1:5000'; // Flask server URL
const BOARD_SIZE = 15;
const EMPTY = 0;

function App() {
  const [board, setBoard] = useState(Array.from({ length: BOARD_SIZE }, () => Array(BOARD_SIZE).fill(EMPTY)));
  const [gameOver, setGameOver] = useState(false);
  const [message, setMessage] = useState('游戏开始，请落子');
  const [isPlayerTurn, setIsPlayerTurn] = useState(true);

  const handleRestart = useCallback(async () => {
    try {
      const response = await fetch(`${API_URL}/api/restart`, { method: 'POST' });
      const data = await response.json();
      setBoard(data.board);
      setGameOver(data.gameOver);
      setMessage(data.message);
      setIsPlayerTurn(true);
    } catch (error) {
      console.error('Error restarting game:', error);
      setMessage('无法连接到服务器。');
    }
  }, []);

  // Fetch initial state on component mount
  useEffect(() => {
    handleRestart();
  }, [handleRestart]);


  const handleCellClick = async (row, col) => {
    if (gameOver || !isPlayerTurn || board[row][col] !== EMPTY) {
      return;
    }

    // Optimistic update for better UX
    const newBoard = board.map(r => [...r]);
    newBoard[row][col] = 1; // Player's stone
    setBoard(newBoard);
    setIsPlayerTurn(false);
    setMessage('AI 正在思考...');

    try {
      const response = await fetch(`${API_URL}/api/move`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ row, col }),
      });
      if (!response.ok) {
          throw new Error('Network response was not ok');
      }
      const data = await response.json();
      setBoard(data.board);
      setGameOver(data.gameOver);
      setMessage(data.message);
      if (!data.gameOver) {
        setIsPlayerTurn(true);
      }
    } catch (error) {
      console.error('Error making move:', error);
      setMessage('与服务器通信失败，请重试。');
      // Revert optimistic update on error
      handleRestart();
    }
  };

  return (
    <div className="app-container">
      <h1>五子棋 - React & Python AI</h1>
      <div className="game-info">
        <p id="msg">{message}</p>
        <button id="restart" onClick={handleRestart}>重新开始</button>
      </div>
      <Board board={board} onCellClick={handleCellClick} disabled={!isPlayerTurn || gameOver} />
    </div>
  );
}

export default App;
