import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  
  // Proteger rotas do PWA de vendedores
  if (pathname.startsWith('/vendedor/app')) {
    // Verificar se há token no cookie ou header
    // No Next.js, não podemos acessar localStorage diretamente no middleware
    // Então verificamos apenas se a rota está sendo acessada
    // A validação real será feita no componente com useVendedor
    
    // Permitir acesso, mas o componente fará a validação
    return NextResponse.next();
  }
  
  // Proteger rota de login de vendedor (apenas se não estiver logado)
  if (pathname.startsWith('/vendedor/login')) {
    return NextResponse.next();
  }
  
  return NextResponse.next();
}

export const config = {
  matcher: [
    '/vendedor/:path*',
  ],
};

