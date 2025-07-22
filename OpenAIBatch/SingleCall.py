import openai
import os
from dotenv import load_dotenv
load_dotenv()


client = openai.AzureOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    api_version="2025-03-01-preview",  # or the version you're using
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)
response = client.responses.create(
    model="gpt-4.1",
    instructions="You are a helpful assistant that creates comprehensive summaries of code snippets.",
    input="""Analyze the following code. Extract and summarize its core functionality, purpose, inputs, outputs, and any significant side effects or business logic.

Provide the summary in a clear, consistent, and language-agnostic structure suitable for direct comparison with other implementations. Use concise and semantically aligned phrasing across summaries.

package com.example.spmigration.processor;

import com.example.spmigration.dto.FirstInputDTO;
import com.example.spmigration.dto.FirstOutputDTO;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;

/**
 * Processor implementation for the "First" bonus calculation logic.
 */
public class FirstBonusProcessor implements IProcessor<FirstInputDTO, FirstOutputDTO> {

    /**
     * Executes the business logic for calculating an employee's bonus.
     * 
     * @param connection Active database connection.
     * @param input      FirstInputDTO with empId.
     * @return           FirstOutputDTO with calculated bonus, status, error messages.
     * @throws Exception If unexpected error occurs.
     */
    @Override
    public FirstOutputDTO execute(Connection connection, FirstInputDTO input) throws Exception {
        Double v_salary = null;
        Double v_total = null;
        int v_count = 0;

        PreparedStatement pstmt = null;
        ResultSet rs = null;

        // Fetch the employee's salary
        try {
            String sql = "SELECT salary FROM employee WHERE employee_id = ?";
            pstmt = connection.prepareStatement(sql);
            pstmt.setInt(1, input.getEmpId());
            rs = pstmt.executeQuery();
            if (rs.next()) {
                v_salary = rs.getDouble("salary");
            } else {
                return new FirstOutputDTO(null, false, "Employee not found: ID " + input.getEmpId());
            }
        } finally {
            if (rs != null) try { rs.close(); } catch (SQLException e) {}
            if (pstmt != null) try { pstmt.close(); } catch (SQLException e) {}
        }

        // Base bonus calculation based on salary
        if (v_salary < 50000) {
            v_total = v_salary + 5000;
        } else {
            v_total = v_salary + 1000;
        }

        // (Future): Integrate bonuses from the 'bonuses' table
        // [The logic is commented out in the PL/SQL, thus not implemented.]

        // WHILE loop: increment v_total by 100, 5 times
        v_count = 0;
        while (v_count < 5) {
            v_total = v_total + 100;
            v_count = v_count + 1;
        }

        return new FirstOutputDTO(v_total, true, null);
    }
}

Return only the following structured bullet-point format:

Purpose/Objective:

Inputs:

Outputs:

Core Logic:

Side Effects (if any):

Business Context (if discernible):"""
)

print(response.output_text)




