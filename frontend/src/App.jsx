import { Routes, Route } from 'react-router-dom';
import Login from './pages/Login';
import Home from './pages/Home';
import MyLists from './pages/MyLists';
import ViewList from './pages/ViewList';
import ViewGroup from './pages/ViewGroup';

function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/lists" element={<MyLists />} />
      <Route path="/lists/:token" element={<ViewList />} />
      <Route path="/groups/:token" element={<ViewGroup />} />
    </Routes>
  );
}

export default App;