import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    
    // Apply email-to-username mapping if needed
    const emailToUsername: { [key: string]: string } = {
      'superadmin@clientiq.com': 'superadmin',
      'admin@acmecorp.com': 'acme_admin',
      'sarah.johnson@acmecorp.com': 'sarah_manager',
      'mike.wilson@acmecorp.com': 'mike_user',
      'emily.davis@acmecorp.com': 'emily_user'
    };
    
    // Map email to username if it's in our mapping
    if (body.username && body.username.includes('@') && emailToUsername[body.username.toLowerCase()]) {
      body.username = emailToUsername[body.username.toLowerCase()];
    }
    
    // Forward the request to Django backend
    const response = await fetch('http://localhost:8000/api/v1/auth/login/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });

    const data = await response.json();

    return NextResponse.json(data, {
      status: response.status,
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization',
      },
    });
  } catch (error) {
    console.error('Proxy error:', error);
    return NextResponse.json(
      { detail: 'Proxy request failed' },
      { 
        status: 500,
        headers: {
          'Access-Control-Allow-Origin': '*',
        },
      }
    );
  }
}

export async function OPTIONS() {
  return new NextResponse(null, {
    status: 200,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    },
  });
}
