import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [result, setResult] = useState(null);

  const handleFileChange = (event) => {
    setSelectedFile(event.target.files[0]);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await axios.post('http://127.0.0.1:5000/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      setResult(response.data);
    } catch (error) {
      console.error('Error uploading file:', error);
    }
  };

  return (
    <div className="App">
      <h1 className="text-3xl font-bold underline">Upload PDF to Extract Details</h1>
      <form onSubmit={handleSubmit}>
        <input type="file" onChange={handleFileChange} />
        <button type="submit">Upload</button>
      </form>
      {result && (
        <div>
          <h2>Student Details</h2>
          <p>Name: {result.name}</p>
          <p>USN: {result.usn}</p>
          <p>Your SGPA for the {result.semester}th semester is {result.sgpa.toFixed(2)}</p>

          <h3>Subjects</h3>
          <ul>
            {result.subjects.map((subject, index) => (
              <li key={index}>
                Subject Code: {subject['Subject Code']}, Subject Name: {subject['Subject Name']}, Total Marks: {subject['Total Marks']}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default App;
