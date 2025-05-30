import { NextResponse } from 'next/server';

export async function GET() {
  try {
    const response = await fetch('http://localhost:8000/dashboard/stats');
    const data = await response.json();

    return NextResponse.json({
      success: true,
      data,
      message: 'Backend API connected successfully',
    });
  } catch (error) {
    return NextResponse.json(
      {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
        message: 'Failed to connect to backend API',
      },
      { status: 500 }
    );
  }
}
