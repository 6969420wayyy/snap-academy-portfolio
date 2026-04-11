
#include <iostream>
#include <vector>
#include <string>
#include <limits>
#include <algorithm>

const int EMPTY  = 0;
const int PAWN   = 1;
const int KNIGHT = 2;
const int BISHOP = 3;
const int ROOK   = 4;
const int QUEEN  = 5;
const int KING   = 6;

typedef std::vector<std::vector<int>> Board;

Board makeStartingBoard() {
    Board b(8, std::vector<int>(8, EMPTY));
    b[0] = { -ROOK, -KNIGHT, -BISHOP, -QUEEN, -KING, -BISHOP, -KNIGHT, -ROOK };
    for (int c = 0; c < 8; c++) b[1][c] = -PAWN;
    b[7] = {  ROOK,  KNIGHT,  BISHOP,  QUEEN,  KING,  BISHOP,  KNIGHT,  ROOK };
    for (int c = 0; c < 8; c++) b[6][c] =  PAWN;
    return b;
}

char pieceChar(int p) {
    const char whites[] = ".PNBRQK";
    const char blacks[] = ".pnbrqk";
    if (p > 0) return whites[p];
    if (p < 0) return blacks[-p];
    return '.';
}

void printBoard(const Board& b) {
    std::cout << "\n  a b c d e f g h\n";
    for (int r = 0; r < 8; r++) {
        std::cout << (8 - r) << " ";
        for (int c = 0; c < 8; c++)
            std::cout << pieceChar(b[r][c]) << " ";
        std::cout << (8 - r) << "\n";
    }
    std::cout << "  a b c d e f g h\n\n";
}

struct Move {
    int r1, c1, r2, c2;
    bool operator==(const Move& o) const {
        return r1==o.r1 && c1==o.c1 && r2==o.r2 && c2==o.c2;
    }
};

std::string moveToStr(const Move& m) {
    std::string s;
    s += (char)('a' + m.c1);
    s += (char)('0' + 8 - m.r1);
    s += (char)('a' + m.c2);
    s += (char)('0' + 8 - m.r2);
    return s;
}

Move strToMove(const std::string& s) {
    Move m;
    m.c1 = s[0] - 'a';
    m.r1 = 8 - (s[1] - '0');
    m.c2 = s[2] - 'a';
    m.r2 = 8 - (s[3] - '0');
    return m;
}

bool inBounds(int r, int c) { return r >= 0 && r < 8 && c >= 0 && c < 8; }
bool isWhite(int p)         { return p > 0; }
bool isBlack(int p)         { return p < 0; }
bool sameColor(int a, int b){ return (a > 0 && b > 0) || (a < 0 && b < 0); }

void addSlidingMoves(const Board& b, int r, int c,
                     const std::vector<std::pair<int,int>>& dirs,
                     std::vector<Move>& moves) {
    int piece = b[r][c];
    for (auto [dr, dc] : dirs) {
        int nr = r + dr, nc = c + dc;
        while (inBounds(nr, nc)) {
            if (sameColor(piece, b[nr][nc])) break;
            moves.push_back({r, c, nr, nc});
            if (b[nr][nc] != EMPTY) break;
            nr += dr; nc += dc;
        }
    }
}

std::vector<Move> generateMoves(const Board& b, bool whiteToMove) {
    std::vector<Move> moves;
    for (int r = 0; r < 8; r++) {
        for (int c = 0; c < 8; c++) {
            int p = b[r][c];
            if (p == EMPTY) continue;
            if (whiteToMove  && isBlack(p)) continue;
            if (!whiteToMove && isWhite(p)) continue;
            int dir = isWhite(p) ? -1 : 1;
            switch (std::abs(p)) {
            case PAWN: {
                int nr = r + dir;
                if (inBounds(nr, c) && b[nr][c] == EMPTY) {
                    moves.push_back({r, c, nr, c});
                    int startRow = isWhite(p) ? 6 : 1;
                    if (r == startRow && b[nr + dir][c] == EMPTY)
                        moves.push_back({r, c, nr + dir, c});
                }
                for (int dc : {-1, 1}) {
                    int nc = c + dc;
                    if (inBounds(nr, nc) && b[nr][nc] != EMPTY && !sameColor(p, b[nr][nc]))
                        moves.push_back({r, c, nr, nc});
                }
                break;
            }
            case KNIGHT: {
                for (auto [dr, dc] : std::vector<std::pair<int,int>>{
                        {-2,-1},{-2,1},{-1,-2},{-1,2},{2,-1},{2,1},{1,-2},{1,2}}) {
                    int nr = r+dr, nc = c+dc;
                    if (inBounds(nr,nc) && !sameColor(p, b[nr][nc]))
                        moves.push_back({r, c, nr, nc});
                }
                break;
            }
            case BISHOP:
                addSlidingMoves(b, r, c, {{-1,-1},{-1,1},{1,-1},{1,1}}, moves);
                break;
            case ROOK:
                addSlidingMoves(b, r, c, {{-1,0},{1,0},{0,-1},{0,1}}, moves);
                break;
            case QUEEN:
                addSlidingMoves(b, r, c, {{-1,-1},{-1,1},{1,-1},{1,1},{-1,0},{1,0},{0,-1},{0,1}}, moves);
                break;
            case KING: {
                for (auto [dr, dc] : std::vector<std::pair<int,int>>{
                        {-1,-1},{-1,0},{-1,1},{0,-1},{0,1},{1,-1},{1,0},{1,1}}) {
                    int nr = r+dr, nc = c+dc;
                    if (inBounds(nr,nc) && !sameColor(p, b[nr][nc]))
                        moves.push_back({r, c, nr, nc});
                }
                break;
            }
            }
        }
    }
    return moves;
}

Board applyMove(Board b, const Move& m) {
    int piece = b[m.r1][m.c1];
    if (std::abs(piece) == PAWN && (m.r2 == 0 || m.r2 == 7))
        piece = (piece > 0) ? QUEEN : -QUEEN;
    b[m.r2][m.c2] = piece;
    b[m.r1][m.c1] = EMPTY;
    return b;
}

const int pieceValue[] = {0, 100, 320, 330, 500, 900, 20000};

int evaluate(const Board& b) {
    int score = 0;
    for (int r = 0; r < 8; r++)
        for (int c = 0; c < 8; c++)
            if (b[r][c] != EMPTY)
                score += (b[r][c] > 0 ? 1 : -1) * pieceValue[std::abs(b[r][c])];
    return score;
}

int minimax(const Board& b, int depth, int alpha, int beta, bool maximising) {
    if (depth == 0) return evaluate(b);
    std::vector<Move> moves = generateMoves(b, maximising);
    if (moves.empty()) return maximising ? -99999 : 99999;
    if (maximising) {
        int best = std::numeric_limits<int>::min();
        for (const Move& m : moves) {
            best = std::max(best, minimax(applyMove(b, m), depth-1, alpha, beta, false));
            alpha = std::max(alpha, best);
            if (beta <= alpha) break;
        }
        return best;
    } else {
        int best = std::numeric_limits<int>::max();
        for (const Move& m : moves) {
            best = std::min(best, minimax(applyMove(b, m), depth-1, alpha, beta, true));
            beta = std::min(beta, best);
            if (beta <= alpha) break;
        }
        return best;
    }
}

Move bestMove(const Board& b, bool whiteToMove, int depth = 3) {
    std::vector<Move> moves = generateMoves(b, whiteToMove);
    Move best = moves[0];
    int bestScore = whiteToMove ? std::numeric_limits<int>::min() : std::numeric_limits<int>::max();
    for (const Move& m : moves) {
        int score = minimax(applyMove(b, m), depth-1,
                            std::numeric_limits<int>::min(),
                            std::numeric_limits<int>::max(), !whiteToMove);
        if ((whiteToMove && score > bestScore) || (!whiteToMove && score < bestScore)) {
            bestScore = score;
            best = m;
        }
    }
    return best;
}

bool isValidInput(const std::string& s) {
    if (s.size() != 4) return false;
    return s[0]>='a' && s[0]<='h' && s[1]>='1' && s[1]<='8' &&
           s[2]>='a' && s[2]<='h' && s[3]>='1' && s[3]<='8';
}

int main() {
    std::cout << "==============================\n";
    std::cout << "   Simple C++ Chess Engine\n";
    std::cout << "==============================\n";
    std::cout << "You play White. Enter moves like: e2e4\n";
    std::cout << "UPPERCASE = White, lowercase = Black\n\n";

    Board board = makeStartingBoard();
    bool whiteToMove = true;

    while (true) {
        printBoard(board);

        if (whiteToMove) {
            std::string input;
            while (true) {
                std::cout << "Your move: ";
                std::cin >> input;
                if (!isValidInput(input)) { std::cout << "Bad format. Use e.g. e2e4\n"; continue; }
                Move m = strToMove(input);
                std::vector<Move> legal = generateMoves(board, true);
                if (std::find(legal.begin(), legal.end(), m) == legal.end()) {
                    std::cout << "Illegal move. Try again.\n"; continue;
                }
                board = applyMove(board, m);
                break;
            }
        } else {
            std::cout << "Engine thinking...\n";
            Move m = bestMove(board, false, 3);
            std::cout << "Engine plays: " << moveToStr(m) << "\n";
            board = applyMove(board, m);
        }

        bool whiteKing = false, blackKing = false;
        for (int r = 0; r < 8; r++)
            for (int c = 0; c < 8; c++) {
                if (board[r][c] ==  KING) whiteKing = true;
                if (board[r][c] == -KING) blackKing = true;
            }
        if (!whiteKing) { printBoard(board); std::cout << "Black wins!\n"; break; }
        if (!blackKing) { printBoard(board); std::cout << "White wins!\n"; break; }
        whiteToMove = !whiteToMove;
    }
    return 0;
}