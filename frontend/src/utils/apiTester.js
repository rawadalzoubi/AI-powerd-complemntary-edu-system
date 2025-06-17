import axios from 'axios';

// API endpoints tester - for development debugging only
const apiTester = {
  // Test the registration endpoint
  testRegister: async () => {
    console.log("Testing registration endpoint...");
    
    try {
      // Try the original registration endpoint
      const response1 = await axios.post('http://localhost:8000/api/user/registration/', {
        test: 'data'
      });
      console.log("Original endpoint /registration/ succeeded:", response1);
      return true;
    } catch (error1) {
      console.log("Original endpoint /registration/ error:", error1.message);
      
      try {
        // Try the new register endpoint
        const response2 = await axios.post('http://localhost:8000/api/user/register/', {
          test: 'data'
        });
        console.log("New endpoint /register/ succeeded:", response2);
        return true;
      } catch (error2) {
        console.log("New endpoint /register/ error:", error2.message);
        
        // Try direct endpoint
        try {
          const response3 = await axios({
            method: 'post',
            url: 'http://localhost:8000/api/user/register/',
            data: { test: 'data' },
            headers: { 'Content-Type': 'application/json' }
          });
          console.log("Direct axios call succeeded:", response3);
          return true;
        } catch (error3) {
          console.log("All registration endpoints failed.");
          console.log("Error details:", error3);
          return false;
        }
      }
    }
  },
  
  // Ping the backend server to check if it's running
  pingServer: async () => {
    try {
      const response = await axios.get('http://localhost:8000/admin/');
      console.log("Server is running, status:", response.status);
      return true;
    } catch (error) {
      console.log("Server ping failed:", error.message);
      return false;
    }
  }
};

export default apiTester; 