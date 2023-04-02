import './App.css';
import Dashboard from './Components/Dashboard';
import {BrowserRouter, Routes, Route} from 'react-router-dom'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path='/' element={<Dashboard/>} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
